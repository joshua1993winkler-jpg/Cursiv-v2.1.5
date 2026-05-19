"""
Babel Agent — Universal language translator.

Encodes any language to UTF-8 binary, decodes and translates to English.
No language needs to be pre-programmed: Python's UTF-8 handles every Unicode
script natively, and the LLM already knows all of them.

Supported automatically: English, Spanish, French, German, Mandarin, Japanese,
Korean, Arabic, Russian, Hindi, Hebrew, Greek, Thai, Vietnamese, and every
other UTF-8 script — same code, zero configuration.
"""

from __future__ import annotations

BABEL_SYSTEM = """You are the Babel Agent — a universal language decoder and translator.

You will receive text encoded as space-separated binary (UTF-8 bytes).
Your protocol:
1. Decode the binary stream byte-by-byte back to its original Unicode text
2. Identify the source language
3. Translate the full content to clear, natural English
4. Add a brief cultural or contextual note only if it genuinely helps understanding

Reply in EXACTLY this format — no extra headers, no markdown, no preamble:
Detected language: [language name]
Original text: [decoded text]
English translation: [translation]
Context: [one sentence if useful, otherwise leave blank]"""


def encode_to_binary(text: str) -> str:
    """
    Encode any text (any language / script) to space-separated UTF-8 binary bytes.
    Example: "こんにちは" → "11100011 10000001 10111011 ..."
    Works for every Unicode language without any per-language configuration.
    """
    return " ".join(f"{b:08b}" for b in text.encode("utf-8"))


def decode_from_binary(binary: str) -> str:
    """Decode space-separated UTF-8 binary bytes back to Unicode text."""
    try:
        bits = binary.strip().split()
        byte_vals = bytes(int(b, 2) for b in bits if len(b) == 8)
        return byte_vals.decode("utf-8")
    except Exception as exc:
        return f"[decode error: {exc}]"


def is_babel_command(text: str) -> bool:
    lower = text.lower().strip()
    return lower.startswith("babel ") or lower.startswith("babel:")


def extract_babel_input(text: str) -> str:
    lower = text.lower().strip()
    for prefix in ("babel:", "babel "):
        if lower.startswith(prefix):
            return text[len(prefix):].strip()
    return text.strip()


def format_binary_block(binary: str, chars_per_line: int = 72) -> str:
    """Wrap long binary string for readable terminal display."""
    words = binary.split()
    lines, current = [], []
    length = 0
    for w in words:
        if length + len(w) + 1 > chars_per_line and current:
            lines.append(" ".join(current))
            current, length = [], 0
        current.append(w)
        length += len(w) + 1
    if current:
        lines.append(" ".join(current))
    return "\n".join(lines)
