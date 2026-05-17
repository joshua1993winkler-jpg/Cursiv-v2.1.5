"""
JWFrontierEvoCore — Terminal Chat
Cursiv-v2.1.5

Run:  python -m cursiv_v215.ui.chat_cli
      OR double-click  Launch Chat CLI.bat

Messages stack naturally and scroll upward — use the mouse wheel or terminal
scroll-bar to read history.  The input box stays at the current bottom.

Commands:
  key  <xai-key>       set xAI Grok API key   (starts with xai-)
  openai <key>         set OpenAI API key      (starts with sk-)
  files on / off       enable / disable file-system access
  workspace <path>     sandbox root for file tools
  mode                 toggle write mode  (auto ↔ confirm)
  clear                wipe conversation history shown in box
  status               show current config
  help                 this list
  exit / Ctrl+C        quit
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
import textwrap
from pathlib import Path

# Force UTF-8 stdout — prevents surrogate/emoji crashes on Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_HERE = Path(__file__).parent
sys.path.insert(0, str(_HERE.parent.parent))

from cursiv_v215.ui.chat_app import (
    WRITE_SENTINEL,
    ROOT,
    chat,
    execute_tool,
)

# ── prompt_toolkit for paste-safe input + wide-char width ──────────────────
# paste-safe: bracketed paste mode so the whole paste lands as one message.
# get_cwidth: correctly counts wide chars (✦ ✓ ✋ etc) as 2 columns so box
#             borders align properly on all terminals.
try:
    from prompt_toolkit import prompt as _pt_prompt
    from prompt_toolkit.formatted_text import ANSI as _PT_ANSI
    from prompt_toolkit.utils import get_cwidth as _cwidth
    _HAS_PT = True
except ImportError:
    _HAS_PT = False
    def _cwidth(c: str) -> int:          # fallback: treat everything as 1
        return 1

# ── Enable ANSI on Windows ─────────────────────────────────────────────────
if os.name == "nt":
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleMode(
            ctypes.windll.kernel32.GetStdHandle(-11), 7)
    except Exception:
        os.system("color")

# ── Palette ────────────────────────────────────────────────────────────────
GOLD  = "\033[38;5;220m"
LGOLD = "\033[38;5;179m"
LAPIS = "\033[38;5;68m"
CREAM = "\033[38;5;230m"
DIM   = "\033[2m"
RED   = "\033[38;5;196m"
GREEN = "\033[38;5;82m"
BOLD  = "\033[1m"
RESET = "\033[0m"

_ANSI = re.compile(r"\033\[[0-9;]*[mABCDEFGHJKST]")


def _vlen(s: str) -> int:
    return sum(_cwidth(c) for c in _ANSI.sub("", s))


def _pad(s: str, w: int) -> str:
    return s + " " * max(0, w - _vlen(s))


def _cols() -> int:
    return max(shutil.get_terminal_size((100, 30)).columns, 52)


# ── Box drawing ────────────────────────────────────────────────────────────

def _top(w: int, label: str) -> str:
    # avail = space for bars only: total width minus 2 corners, 2 spaces, label
    avail = w - 4 - _vlen(label)
    side  = max(avail // 2, 1)
    extra = "═" if avail % 2 else ""
    bar   = "═" * side
    return f"{LGOLD}╔{bar} {GOLD}{BOLD}{label}{RESET}{LGOLD} {bar}{extra}╗{RESET}"


def _mid(w: int, ch: str = "═") -> str:
    return f"{LGOLD}╠{ch * (w - 2)}╣{RESET}"


def _bot(w: int) -> str:
    return f"{LGOLD}╚{'═' * (w - 2)}╝{RESET}"


def _row(content: str, w: int) -> str:
    inner = w - 4
    return f"{LGOLD}║{RESET} {_pad(content, inner)} {LGOLD}║{RESET}"


def _sep(w: int) -> str:
    return f"  {DIM}{'·' * (w - 4)}{RESET}"


# ── Status header (printed at startup and when settings change) ────────────

def _print_header(cfg: dict) -> None:
    w      = _cols()
    xai_s  = f"{GREEN}xAI:OK{RESET}"    if cfg["api_key"]    else f"{DIM}xAI:--{RESET}"
    oai_s  = f"{GREEN}OpenAI:OK{RESET}" if cfg["openai_key"] else f"{DIM}OpenAI:--{RESET}"
    fa_s   = f"{GREEN}files:ON{RESET}"  if cfg["file_access"] else f"{DIM}files:OFF{RESET}"
    mode_s = (f"{RED}CONFIRM[!]{RESET}" if cfg["confirm_mode"] == "confirm"
              else f"{DIM}AUTO{RESET}")
    status = f"  {xai_s}  ·  {oai_s}  ·  {fa_s}  ·  mode:{mode_s}  ·  {DIM}'help'{RESET}"
    print(_top(w, "✦  JWFrontierEvoCore  ✦"))
    print(_row(status, w))
    print(_bot(w))
    print()


# ── Message printing ───────────────────────────────────────────────────────

def _print_ai_msg(text: str) -> None:
    w      = _cols()
    wrap_w = max(w - 14, 20)
    pfx0   = f"  {GOLD}{BOLD}  ✦ AI{RESET}  "
    pfxN   = "          "
    first  = True
    for para in text.splitlines():
        if not para.strip():
            print()
            first = True
            continue
        for seg in textwrap.wrap(para, width=wrap_w) or [""]:
            pfx = pfx0 if first else pfxN
            print(f"{pfx}{GOLD}{seg}{RESET}")
            first = False


def _print_user_msg(text: str) -> None:
    w = _cols()
    print(f"\n  {LAPIS}{BOLD}You  ❯{RESET}  {CREAM}{text}{RESET}")
    print(_sep(w))
    print()


# ── Input prompt box ───────────────────────────────────────────────────────

def _input_prompt(cfg: dict) -> str:
    """
    Print the bottom input box and return whatever the user types.
    Uses prompt_toolkit when available — enables bracketed paste mode so
    multiline pastes land as a single message rather than firing line-by-line.
    Falls back to plain input() if prompt_toolkit is not installed.
    """
    w      = _cols()
    inner  = w - 6
    mode_s = (f"{RED}CONFIRM[!]{RESET}" if cfg["confirm_mode"] == "confirm"
              else f"{DIM}AUTO{RESET}")
    hint   = _pad(f"  mode:{mode_s}  ·  Ctrl+C to exit", inner)

    print(f"\n  {LGOLD}╭{'─' * inner}╮{RESET}")
    print(f"  {LGOLD}│{RESET}{hint}{LGOLD}│{RESET}")
    print(f"  {LGOLD}├{'─' * inner}┤{RESET}")

    # The prompt prefix printed before the cursor
    prefix_ansi = f"  {LGOLD}│{RESET}  {LAPIS}{BOLD}❯{RESET}  "

    try:
        if _HAS_PT:
            # prompt_toolkit handles bracketed paste — multiline paste = one block
            raw = _pt_prompt(_PT_ANSI(prefix_ansi))
        else:
            sys.stdout.write(prefix_ansi)
            sys.stdout.flush()
            raw = input("")
    except (EOFError, KeyboardInterrupt):
        raise KeyboardInterrupt

    print(f"  {LGOLD}╰{'─' * inner}╯{RESET}")
    return raw.strip()


# ── Pending-write confirm ──────────────────────────────────────────────────

def _handle_pending_write(raw_json: str, cfg: dict) -> str:
    try:
        pending = json.loads(raw_json)
    except Exception:
        return "[Could not parse pending write]"

    path_str = pending.get("path", "?")
    content  = pending.get("content", "")
    preview  = content[:400] + ("..." if len(content) > 400 else "")

    w = _cols()
    print(f"\n  {RED}{BOLD}Write pending → {path_str}{RESET}")
    print(f"  {DIM}{'─' * (w - 4)}{RESET}")
    for line in preview.splitlines():
        print(f"  {DIM}{line}{RESET}")
    print(f"  {DIM}{'─' * (w - 4)}{RESET}\n")

    while True:
        try:
            if _HAS_PT:
                ans = _pt_prompt(_PT_ANSI(f"  {RED}Approve write?{RESET}  [y/n]: ")).strip().lower()
            else:
                ans = input(f"  {RED}Approve write?{RESET}  [y/n]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            ans = "n"
        if ans in ("y", "yes"):
            workspace = Path(cfg["workspace"]).expanduser().resolve()
            result    = execute_tool("write_file", pending, workspace)
            print(f"\n  {GREEN}✓ {result}{RESET}\n")
            return f"Write approved.\n{result}"
        elif ans in ("n", "no", ""):
            print(f"\n  {DIM}Write cancelled.{RESET}\n")
            return "Write cancelled — file not modified."
        else:
            print("  y or n.")


# ── Built-in command responses ─────────────────────────────────────────────

_HELP = f"""\
  {LGOLD}key  <xai-key>{RESET}       set xAI Grok API key   (starts with xai-)
  {LGOLD}openai <key>{RESET}         set OpenAI API key      (starts with sk-)
  {LGOLD}files on / off{RESET}       enable / disable file-system access
  {LGOLD}workspace <path>{RESET}     sandbox root for file tools
  {LGOLD}mode{RESET}                 toggle write mode  (auto ↔ confirm)
  {LGOLD}clear{RESET}                wipe conversation history
  {LGOLD}status{RESET}               show current config
  {LGOLD}help{RESET}                 this list
  {LGOLD}exit{RESET}                 quit"""


def _status_str(cfg: dict) -> str:
    return (
        f"  xAI key    : {'set ✓' if cfg['api_key']    else 'not set ✗'}\n"
        f"  OpenAI key : {'set ✓' if cfg['openai_key'] else 'not set ✗'}\n"
        f"  File access: {'ON'   if cfg['file_access'] else 'OFF'}\n"
        f"  Write mode : {cfg['confirm_mode'].upper()}\n"
        f"  Workspace  : {cfg['workspace']}"
    )


# ── Main ───────────────────────────────────────────────────────────────────

def main() -> None:
    cfg: dict = {
        "api_key":      os.environ.get("XAI_API_KEY",    ""),
        "openai_key":   os.environ.get("OPENAI_API_KEY", ""),
        "file_access":  False,
        "confirm_mode": "confirm",   # always ask before writing — type 'mode' to switch to auto
        "workspace":    str(ROOT),
    }

    # Auto-fix swapped env-var keys
    if cfg["api_key"].startswith("sk-") or cfg["api_key"].startswith("sk_"):
        cfg["openai_key"] = cfg["openai_key"] or cfg["api_key"]
        cfg["api_key"] = ""
    if cfg["openai_key"].startswith("xai-"):
        cfg["api_key"] = cfg["api_key"] or cfg["openai_key"]
        cfg["openai_key"] = ""

    history: list[dict] = []

    _print_header(cfg)

    hints = []
    if not cfg["api_key"]:
        hints.append(f"  No xAI key.    Type:  {LGOLD}key xai-xxxxxxxx{RESET}  (console.x.ai)")
    if not cfg["openai_key"]:
        hints.append(f"  No OpenAI key. Type:  {LGOLD}openai sk-xxxxxxxx{RESET}  (platform.openai.com)")
    hints.append(f"  {RED}Write mode: CONFIRM ✋  — you must approve every file write.{RESET}")
    hints.append(f"  {DIM}Type 'mode' to switch to AUTO (writes without asking).{RESET}")
    hints.append(f"  {DIM}Scroll up to read history.  'help' for all commands.{RESET}")
    for h in hints:
        print(h)

    while True:
        # ── Input ────────────────────────────────────────────────────────
        try:
            raw = _input_prompt(cfg)
        except KeyboardInterrupt:
            print(f"\n\n  {DIM}Goodbye.{RESET}\n")
            break

        if not raw:
            continue

        cmd = raw.lower()

        # ── Built-in commands ────────────────────────────────────────────
        if cmd == "exit":
            print(f"\n  {DIM}Goodbye.{RESET}\n")
            break

        elif cmd == "help":
            print(_HELP)
            continue

        elif cmd == "clear":
            history = []
            _print_header(cfg)
            print(f"  {DIM}History cleared.{RESET}")
            continue

        elif cmd == "mode":
            cfg["confirm_mode"] = "confirm" if cfg["confirm_mode"] == "auto" else "auto"
            print(f"  Write mode → {cfg['confirm_mode'].upper()}")
            continue

        elif cmd == "status":
            print(_status_str(cfg))
            continue

        elif cmd.startswith("key "):
            new_key = raw[4:].strip()
            if new_key.startswith("sk-") or new_key.startswith("sk_"):
                cfg["openai_key"] = new_key
                print(f"  {DIM}That's an OpenAI key — routed to the OpenAI slot. ✓{RESET}")
                print(f"  {DIM}xAI keys start with  xai-  (console.x.ai){RESET}")
            else:
                cfg["api_key"] = new_key
                print(f"  {GREEN}xAI key set. ✓{RESET}")
            _print_header(cfg)
            continue

        elif cmd.startswith("openai "):
            new_key = raw[7:].strip()
            if new_key.startswith("xai-"):
                cfg["api_key"] = new_key
                print(f"  {DIM}That's an xAI key — routed to the xAI slot. ✓{RESET}")
                print(f"  {DIM}OpenAI keys start with  sk-  (platform.openai.com){RESET}")
            else:
                cfg["openai_key"] = new_key
                print(f"  {GREEN}OpenAI key set. ✓{RESET}")
            _print_header(cfg)
            continue

        elif cmd.startswith("workspace "):
            cfg["workspace"] = raw[10:].strip()
            print(f"  Workspace → {cfg['workspace']}")
            continue

        elif cmd in ("files on", "files off"):
            cfg["file_access"] = cmd == "files on"
            print(f"  File access → {'ON' if cfg['file_access'] else 'OFF'}")
            continue

        # ── Send to model ────────────────────────────────────────────────
        history.append({"role": "user", "content": raw})
        _print_user_msg(raw)

        # AI prefix — stream tokens directly below it
        w     = _cols()
        pfx0  = f"  {GOLD}{BOLD}  ✦ AI{RESET}  "
        pfxN  = "          "
        sys.stdout.write(pfx0)
        sys.stdout.flush()

        full_response   = ""
        pending_payload = None
        line_len        = 0          # visible chars on the current output line
        wrap_w          = max(w - 14, 20)
        first_line      = True

        try:
            for chunk in chat(
                raw,
                history[:-1],
                cfg["api_key"],
                None,
                cfg["file_access"],
                cfg["workspace"],
                cfg["openai_key"],
                cfg["confirm_mode"] == "confirm",
            ):
                combined = full_response + chunk
                if WRITE_SENTINEL in combined:
                    display, raw_json = combined.split(WRITE_SENTINEL, 1)
                    # Print whatever came before the sentinel
                    leftover = display[len(full_response):]
                    if leftover:
                        sys.stdout.write(f"{GOLD}{leftover}{RESET}")
                        sys.stdout.flush()
                    full_response   = display
                    pending_payload = raw_json
                    break

                # Simple direct streaming — terminal wraps naturally
                sys.stdout.write(f"{GOLD}{chunk}{RESET}")
                sys.stdout.flush()
                full_response = combined

        except KeyboardInterrupt:
            full_response = full_response or "(interrupted)"

        print()   # newline after streamed response
        print()

        # ── Handle pending write ─────────────────────────────────────────
        if pending_payload is not None:
            result        = _handle_pending_write(pending_payload, cfg)
            full_response = full_response.rstrip() + f"\n\n{result}"
            print(f"  {GOLD}{result}{RESET}\n")

        history.append({"role": "assistant", "content": full_response})


if __name__ == "__main__":
    main()
