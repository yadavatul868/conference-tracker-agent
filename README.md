# AI/ML Conference Tracker

A minimal agentic CLI tool that uses a **local Ollama model** + **DuckDuckGo search**
to find upcoming AI/ML conferences, CFP deadlines, and submission categories.

No API keys. No cloud. Runs entirely on your machine.

---

## How it works

```
You run the script
      ↓
Ollama LLM decides what to search
      ↓
DuckDuckGo fetches live results
      ↓
LLM reflects → searches again if needed (up to 6 rounds)
      ↓
LLM writes a structured markdown report
      ↓
Saved to conferences.md
```

---

## Setup

### 1. Install Ollama
```bash
# macOS
brew install ollama

# Or download from https://ollama.com
```

### 2. Pull a model
```bash
# Recommended (good tool-calling support)
ollama pull llama3.1:8b

# Alternatives
ollama pull mistral:7b
ollama pull qwen2.5:7b     # strong tool use
```

### 3. Create and activate a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
.venv\Scripts\activate         # Windows
```

### 4. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure environment (optional)
```bash
cp .env.example .env
# Edit .env to override defaults
```

---

## Usage

```bash
# Basic run (uses llama3.1:8b, broad AI/ML focus)
python conference_tracker.py

# Specify a model
python conference_tracker.py --model mistral:7b

# Focus on a specific topic
python conference_tracker.py --topic "healthcare AI and clinical NLP"

# Custom output file
python conference_tracker.py --output my_conferences.md

# All options
python conference_tracker.py --model qwen2.5:7b --topic "LLM agents and applied AI" --output llm_cfps.md
```

---

## Output

A markdown file (`conferences.md`) with a structured list of conferences including:
- Conference name and abbreviation
- Submission deadline
- Notification date
- Event date and location
- Relevant tracks / categories
- Website link

---

## Model recommendations

| Model | RAM needed | Tool-calling | Notes |
|-------|-----------|--------------|-------|
| `llama3.1:8b` | ~8GB | ✅ Good | Best balance for 16GB M-series |
| `qwen2.5:7b` | ~8GB | ✅ Excellent | Strong at structured output |
| `mistral:7b` | ~8GB | ⚠️ OK | May need re-prompting |
| `phi3.5:mini` | ~4GB | ⚠️ Limited | Use only if RAM is tight |

---

## Project structure

```
conference-tracker-agent/
├── conference_tracker.py   # main agent script
├── requirements.txt        # Python dependencies
├── .env.example            # environment variable template
├── .gitignore
└── README.md
```

---

## Roadmap

- [ ] Deadline alerts — warn when a CFP deadline is within 30 days
- [ ] Export to CSV / JSON for calendar import
- [ ] Schedule as a weekly cron job
- [ ] Abstract-matching pass — paste your paper abstract, model scores fit per conference
- [ ] Multi-model support via config file
