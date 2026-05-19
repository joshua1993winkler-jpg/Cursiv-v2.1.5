# ⬡ Cursiv — Rolling Updates

Code-only changes that do not require a new installer binary.
Pull from GitHub and restart Cursiv — changes are live immediately.

For releases that include a new `.exe`, see [CHANGELOG.md](CHANGELOG.md).

---

## 2026-05-19 — v3.14-U02 patch set

These changes shipped as `git push` — no new binary required. Pull and restart.

### Real-Time Web Search
- `_web_search()` / `_ddg_search()` / `_brave_search()` added to `chat_app.py`
- DuckDuckGo Instant Answer API + Lite HTML fallback — worldwide, zero config, zero cost
- Optional Brave Search API upgrade: set `BRAVE_API_KEY` in `secrets.bat` (2,000 free queries/month)
- Auto-fires on trigger phrases: "latest", "today", "who won", "price of", "breaking", etc.
- Explicit command: `search: <query>` or `search <query>` in terminal
- Results injected into system prompt before every provider — all providers see live facts

### Babel Agent
- New file: `cursiv_v215/agents/babel_agent.py`
- `encode_to_binary()` — any Unicode text → space-separated UTF-8 binary bytes
- `decode_from_binary()` — Python decodes binary (always perfect, handles all scripts)
- LLM receives decoded text and translates to English — no manual binary decoding by the model
- Works for every language with zero per-language configuration: Japanese, Arabic, Chinese, Russian, Hindi, etc.
- Terminal command: `babel <text in any language>`

### Group Discovery
- `_call_group_discovery()` added to `chat_app.py`
- Four providers in sequence: Cursiv (Ollama) → xAI → OpenAI → Claude
- Each provider receives all prior responses as context — builds on, not duplicates
- Cursiv participates as first voice (uninfluenced baseline), not just a bridge
- Synthesis pass: Agreements / Disagreements (Weighted) / Synthesis Notes
- Binary snapshot at end — shareable, decodable by any Cursiv instance
- Terminal: `council <question>` · Gradio: "Group Discovery" in provider dropdown

### FunForge Meta
- New file: `cursiv_v215/forge/funforge_meta.py`
- 45-minute bounded creative spike with timer in terminal status bar
- `funforge <topic>` / `spike <topic>` to start · `forge extend` (+30 min once) · `forge done` · `anchor this`
- Produces exact 5-line closing artifact: Focus / What happened / Keep / State / Next spark

### Offline Routing Fix
- `_is_online()` — TCP connect to 8.8.8.8:53, 2s timeout — gates all cloud routing
- Short-circuits directly to Ollama when offline — no false cloud errors in airplane mode
- `_fa_error()` updated to catch RATE_SENTINEL, `getaddrinfo failed`, `urlopen error`

### Auto-Generated Live System Status
- `_build_live_status()` added to `chat_app.py`
- Appended to every system prompt at runtime — reflects actual loaded modules and env vars
- Reads version from `launcher/cursiv_launcher.py` source directly
- No manual `system_prompt.md` edits needed when adding new agents or tools
- `system_prompt.md` updated to v3.14-U02 with accurate capabilities block

### Winkler-Codex Download
- "Winkler-Codex Download" button added to launcher window and tray menu
- Pulls `qwen2.5-coder:14b` + `deepseek-coder-v2:16b` via Ollama (~18 GB total)
- Models review each other's work before output surfaces

---

## How to Apply Any Update

**From source (git):**
```
git pull origin main
```
Restart Cursiv. No reinstall. No binary. Changes are live.

**From installer:**
Open Cursiv launcher → Check for Updates → Download & Install.
Ollama, llama3.1, and all `.cursiv/` data are untouched.

---

*Rolling updates are tracked here so you know exactly what changed between installer releases.*
*For full release notes see [RELEASE_v3.md](RELEASE_v3.md).*
*For the full technical breakdown see [TECH.md](TECH.md).*
