"""
AI/ML Conference Tracker — v1
Uses a local Ollama model + DuckDuckGo search to find upcoming conferences,
CFP deadlines, and submission categories.

Usage:
    python conference_tracker.py
    python conference_tracker.py --model mistral:7b
    python conference_tracker.py --topic "healthcare AI"
"""

import json
import argparse
from datetime import datetime
from duckduckgo_search import DDGS
import ollama

# ── Config ──────────────────────────────────────────────────────────────────

DEFAULT_MODEL = "llama3.1:8b"
MAX_SEARCH_RESULTS = 5
MAX_TOOL_ROUNDS = 6          # max search→reflect loops before forcing a summary
OUTPUT_FILE = "conferences.md"

# ── Tool: web search ─────────────────────────────────────────────────────────

def web_search(query: str) -> str:
    """Run a DuckDuckGo search and return formatted snippets."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=MAX_SEARCH_RESULTS))
        if not results:
            return "No results found."
        lines = []
        for r in results:
            lines.append(f"Title: {r.get('title', '')}")
            lines.append(f"URL:   {r.get('href', '')}")
            lines.append(f"Body:  {r.get('body', '')}")
            lines.append("---")
        return "\n".join(lines)
    except Exception as e:
        return f"Search error: {e}"


# Tool schema for Ollama (OpenAI-compatible format)
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "Search the web for current information about AI/ML conferences, "
                "CFP deadlines, submission dates, and event details."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "A specific search query, e.g. 'NeurIPS 2025 submission deadline'",
                    }
                },
                "required": ["query"],
            },
        },
    }
]

# ── Agent loop ────────────────────────────────────────────────────────────────

def run_agent(model: str, topic: str) -> str:
    """
    Agentic loop:
      1. LLM decides what to search
      2. We run the search and return results
      3. LLM reflects and either searches again or writes the final report
    Returns the final markdown report string.
    """
    today = datetime.today().strftime("%B %d, %Y")

    system_prompt = f"""You are a research assistant helping an AI/ML engineer track conferences.
Today is {today}.

Your job:
1. Use the web_search tool to find upcoming AI/ML conferences (2025–2026).
2. Focus on: {topic}
3. For each conference collect: full name, short name, submission deadline,
   notification date, event date, location, website, and relevant tracks/categories.
4. After gathering enough data (4–6 searches), write a clean, structured markdown report.

Be systematic — search for different conference families (ML, NLP, Health AI, Applied AI, Agents).
When you have enough data, stop searching and write the final report."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Find upcoming AI/ML conferences relevant to: {topic}. Start searching now."}
    ]

    print(f"\n{'─'*60}")
    print(f"  Model  : {model}")
    print(f"  Topic  : {topic}")
    print(f"  Date   : {today}")
    print(f"{'─'*60}\n")

    for round_num in range(1, MAX_TOOL_ROUNDS + 1):
        print(f"[round {round_num}] calling model...")

        response = ollama.chat(
            model=model,
            messages=messages,
            tools=TOOLS,
        )

        msg = response["message"]
        messages.append(msg)

        # No tool calls → model is done, extract final text
        if not msg.get("tool_calls"):
            final_text = msg.get("content", "").strip()
            if final_text:
                print(f"[round {round_num}] model finished — writing report.\n")
                return final_text
            else:
                # Empty response with no tool calls — prompt for summary
                print(f"[round {round_num}] empty response — prompting for summary...")
                messages.append({
                    "role": "user",
                    "content": "Please now write the final markdown report with all conferences you found."
                })
                continue

        # Execute each tool call the model requested
        for tool_call in msg["tool_calls"]:
            fn_name = tool_call["function"]["name"]
            fn_args = tool_call["function"]["arguments"]

            if isinstance(fn_args, str):
                fn_args = json.loads(fn_args)

            query = fn_args.get("query", "")
            print(f"  → searching: {query}")
            result = web_search(query)

            messages.append({
                "role": "tool",
                "content": result,
            })

    # Exceeded max rounds — ask for whatever the model has
    print("[agent] max rounds reached — requesting final summary...")
    messages.append({
        "role": "user",
        "content": "You've done enough research. Write the final markdown report now with whatever you have."
    })
    response = ollama.chat(model=model, messages=messages)
    return response["message"].get("content", "No report generated.")


# ── Output ────────────────────────────────────────────────────────────────────

def save_report(content: str, filepath: str):
    header = f"""# AI/ML Conference Tracker
_Generated on {datetime.today().strftime("%B %d, %Y")} using local Ollama model_

---

"""
    with open(filepath, "w") as f:
        f.write(header + content)
    print(f"Report saved → {filepath}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="AI/ML Conference Tracker (Ollama + DuckDuckGo)")
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Ollama model to use (default: {DEFAULT_MODEL})"
    )
    parser.add_argument(
        "--topic",
        default="applied AI, healthcare AI, NLP, general ML research",
        help="Research focus area"
    )
    parser.add_argument(
        "--output",
        default=OUTPUT_FILE,
        help=f"Output markdown file (default: {OUTPUT_FILE})"
    )
    args = parser.parse_args()

    report = run_agent(model=args.model, topic=args.topic)
    save_report(report, args.output)

    # Print a preview
    print("\n" + "─"*60)
    print("PREVIEW (first 60 lines):")
    print("─"*60)
    for line in report.splitlines()[:60]:
        print(line)
    if len(report.splitlines()) > 60:
        print(f"\n... ({len(report.splitlines()) - 60} more lines in {args.output})")


if __name__ == "__main__":
    main()
