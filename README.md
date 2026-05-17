# ⬡ JWFrontierEvoCore — Cursiv v2.1.5

> **An autonomous AI operating system built for one purpose: executing at the frontier.**
> Dual-model intelligence (xAI Grok + OpenAI GPT-4.1), live file tools, a 14-agent council, and a full terminal interface — all running locally on your machine.

<br>

---

## 🌟 What Is This?

**JWFrontierEvoCore** is a self-contained AI workspace that wires together the best of xAI and OpenAI into a single, sovereign system. It's not a wrapper — it's a full operating environment:

- 💬 **Main Chat UI** — Sacred-aesthetic Gradio interface, streaming AI responses, image and file uploads
- 🖥️ **Terminal Chat** — Full-screen CLI with ANSI gold/lapis styling, paste-safe input, no browser needed
- 🧠 **Nexus Panel** — 14-agent command council with live status, yin-yang balance tracking, and identity drift monitoring
- 🔧 **File System Tools** — AI reads, writes, searches, and organizes your codebase autonomously
- ✋ **Confirm-Before-Write** — Every file write requires your approval before execution (toggleable)
- 🎓 **Training Pipeline** — Save any conversation exchange to a JSONL training dataset with one click
- 📦 **Vault + Academy** — Agent memory, LoRA training metadata, and performance scoring built in

<br>

---

## ⚡ Quick Start — One Click

**Prerequisites:** Python 3.10+ and pip installed.

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/Cursiv-v2.1.5.git
cd Cursiv-v2.1.5
```

### 2. Run setup
Double-click **`Setup and Launch Cursiv.bat`**

*Installs all dependencies automatically — no manual pip commands needed.*

### 3. Add your API keys
Create a file called **`secrets.bat`** in the project root:
```bat
@echo off
set XAI_API_KEY=xai-your-key-here
set OPENAI_API_KEY=sk-your-key-here
```

> **Get your keys:**
> - xAI Grok → [console.x.ai](https://console.x.ai)
> - OpenAI GPT-4.1 → [platform.openai.com](https://platform.openai.com)

### 4. Launch
| What | How |
|------|-----|
| 🖥️ Terminal Chat *(recommended)* | Double-click **`Launch Chat CLI.bat`** |
| 💬 Gradio Web UI | Double-click **`Launch Chat.bat`** → open `http://localhost:7860` |
| ⬡ Nexus Panel | Double-click **`Launch Nexus.bat`** → open `http://localhost:7861` |
| 🚀 Everything at once | Double-click **`START CURSIV SYSTEM.bat`** |

<br>

---

## 🔑 API Keys — Your Options

You have three ways to configure keys. Pick one:

**Option A — `secrets.bat` *(recommended, git-ignored)***
Create `secrets.bat` in the project root as shown above. It loads automatically on every launch.

**Option B — System environment variables**
Set `XAI_API_KEY` and `OPENAI_API_KEY` in Windows System Properties → Advanced → Environment Variables. Picked up automatically with no extra steps.

**Option C — Enter manually in the chat**
In Terminal Chat, type:
```
key xai-xxxxxxxx
openai sk-xxxxxxxx
```
In the Gradio UI, paste into the key slots at the top of the page.

> ⚠️ `secrets.bat` is listed in `.gitignore` — it will **never** be committed or pushed. Your keys stay on your machine only.

<br>

---

## 🖥️ Terminal Chat — Commands

Once inside the terminal chat:

| Command | What it does |
|---------|-------------|
| `key xai-xxx` | Set xAI Grok API key |
| `openai sk-xxx` | Set OpenAI API key |
| `files on` / `files off` | Enable / disable file system access |
| `workspace <path>` | Set the sandbox root for file operations |
| `mode` | Toggle write mode: CONFIRM ✋ ↔ AUTO ⚡ |
| `status` | Show current config (keys, mode, workspace) |
| `clear` | Wipe conversation history |
| `help` | List all commands |
| `exit` / `Ctrl+C` | Quit |

> 💡 **Tip:** Paste multi-line prompts freely — the terminal uses `prompt_toolkit` for paste-safe input. Your entire paste lands as one message.

<br>

---

## 🔧 File System Tools

When `files on` is active, the AI has access to these tools:

| Tool | Description |
|------|-------------|
| `submit_plan` | AI submits a full build plan before writing anything |
| `read_file` | Read any file in the workspace |
| `write_file` | Create or overwrite a file |
| `list_directory` | List files and folders |
| `search_files` | Glob pattern search (e.g. `**/*.py`) |
| `create_directory` | Create a directory tree |
| `delete_file` | Delete a file |

All file operations are **sandboxed** to the workspace root. No path can escape the sandbox — escaping attempts are blocked at the resolver level before any I/O occurs.

**Write modes:**
- ✋ **CONFIRM** *(default)* — AI shows you the file content and waits for `y/n` before writing anything
- ⚡ **AUTO** — Writes execute immediately. Toggle with `mode` in terminal or `Ctrl+\`` in the web UI.

<br>

---

## 🧠 Dual-Model Architecture

```
User message
     │
     ▼
xAI Grok-3 ──── plans · reasons · calls file tools · generates drafts
     │
     ▼  (on every write_file)
OpenAI GPT-4.1 ── reads full conversation context · rewrites to production quality
     │
     ▼
File written to disk  (after your ✋ approval)
```

- **Grok** handles conversation, planning, and the agentic tool loop (up to 20 iterations, 4,000 tokens per call)
- **GPT-4.1** intercepts every file write, pulls in the last 6 conversation turns for context, and generates final production-ready code with no stubs or TODOs
- If OpenAI is unavailable, Grok's draft is written directly as fallback
- If neither key is set, falls back to local **Ollama** (install `ollama pull mistral` for offline use)

<br>

---

## ⬡ The Nexus Panel

The Nexus (`http://localhost:7861`) is your command center:

- **14-Agent Council** — Assign agents to domains and tasks; assignments inject into the main chat automatically on your next message
- **Yin-Yang Balance** — 7 axes tracked in real time (depth/speed, structure/flow, individual/civilization, and more)
- **Identity Drift Monitor** — Constitutional guardrails with a 3% abort threshold and verified invariants
- **Training Dashboard** — View, manage, and export your conversation training dataset
- **Full Cycle** — Run all 8 JW Architect phases (Energy → Emergency → Grounding → Route → Structure → Connectivity → Future State → Recovery)

<br>

---

## 📁 Project Structure

```
Cursiv-v2.1.5/
├── cursiv_v215/
│   ├── ui/
│   │   ├── chat_app.py        # Gradio main chat (port 7860)
│   │   ├── chat_cli.py        # Terminal chat
│   │   └── nexus_app.py       # Nexus command panel (port 7861)
│   ├── core/                  # Agent, memory, constitution engine
│   ├── council/               # 14-agent deliberation system
│   ├── forge/                 # Training data forge + factory
│   ├── academy/               # Scoring and LoRA pipeline
│   ├── dugout/                # Agent vault
│   ├── weave/                 # Sovereign + transitionary weave
│   └── nexus/                 # Command router
├── Launch Chat CLI.bat        # ← Start here for terminal mode
├── Launch Chat.bat            # Gradio web UI launcher
├── Launch Nexus.bat           # Nexus panel launcher
├── START CURSIV SYSTEM.bat    # Launch everything at once
├── Setup and Launch Cursiv.bat
├── secrets.bat                # YOUR KEYS — create this (git-ignored)
├── requirements.txt
└── .gitignore
```

<br>

---

## 📦 Requirements

```
Python 3.10+
gradio >= 4.44.0
prompt_toolkit >= 3.0.0
```

Optional for expanded functionality:
- **Ollama** — fully offline operation without API keys (`ollama pull mistral`)
- **pypdf** — PDF file reading and upload support

<br>

---

## 🛡️ Security Model

- All file operations are sandboxed to the configured workspace root using Python's `Path.relative_to()` — path traversal is structurally impossible
- API keys are read from environment variables only — never logged, stored in history, or sent anywhere except the respective API endpoint
- `secrets.bat` is explicitly excluded from git via `.gitignore` and will never appear in commits or pushes
- **CONFIRM** write mode is the default — no file is ever modified without your explicit `y` approval at the terminal

<br>

---

## 🚀 Offline Mode

No API keys? Run fully locally with Ollama:

```bash
# 1. Install Ollama from https://ollama.com
# 2. Pull the model
ollama pull mistral

# 3. Launch the chat — it falls back to Mistral automatically
```

<br>

---

## 📜 License & Copyright

Copyright © 2026 Joshua Winkler. All rights reserved.

This software is released under the MIT License. See [LICENSE](LICENSE) for full terms.

<br>

---

*Built by Joshua Winkler · JWFrontierEvoCore v1.0 · Cursiv-v2.1.5*
