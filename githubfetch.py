#!/usr/bin/env python3
"""
Show a GitHub user’s avatar + profile data, side-by-side, in true-colour ASCII.
"""

import os
import sys
import io
import textwrap
import requests
from PIL import Image

# ──────────────────────────────────────────────────────────────────── Colours ──
class Color:
    def __init__(self):
        self.red        = "\033[91m"
        self.green      = "\033[92m"
        self.yellow     = "\033[93m"
        self.light_blue = "\033[94m"
        self.light_red  = "\033[95m"
        self.blue       = "\033[96m"
        self.reset      = "\033[0m"

    def paint(self, colour_code, text):
        return f"{colour_code}{text}{self.reset}"


# ──────────────────────────────────────────────────────────────── ANSI on Win ──
def enable_ansi_colors():
    """Enable ANSI escape sequences on Windows terminals."""
    if os.name == "nt":                        # only Windows needs this
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            handle   = kernel32.GetStdHandle(-11)    # STD_OUTPUT_HANDLE = -11
            kernel32.SetConsoleMode(handle, 7)       # ENABLE_VIRTUAL_TERMINAL
        except Exception:
            pass


# ────────────────────────────────────────────────────────────── Avatar helper ──
def display_avatar(avatar_url, colour):
    """Return a list of strings, each representing one row of coloured blocks."""
    try:
        r = requests.get(avatar_url, timeout=10)
        r.raise_for_status()
        img = Image.open(io.BytesIO(r.content)).convert("RGB").resize((18, 18))

        art_rows = []
        for y in range(img.height):
            row_fragments = []
            for x in range(img.width):
                r_, g_, b_ = img.getpixel((x, y))
                true_col   = f"\033[38;2;{r_};{g_};{b_}m"
                row_fragments.append(f"{true_col}██{colour.reset}")
            art_rows.append("".join(row_fragments))
        return art_rows
    except Exception:
        return []


# ─────────────────────────────────────────────────────────────────────  MAIN ──
def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <github-user>")
        sys.exit(1)

    enable_ansi_colors()
    colour   = Color()
    username = sys.argv[1]

    print(f"Fetching GitHub profile for: {username}")
    url  = f"https://api.github.com/users/{username}"
    resp = requests.get(url, timeout=10)

    if resp.status_code == 404:
        print(colour.paint(colour.red, f"Error: user '{username}' not found."))
        sys.exit(1)
    elif not resp.ok:
        print(colour.paint(colour.red, f"GitHub API error: {resp.status_code}"))
        sys.exit(1)

    data        = resp.json()
    avatar_rows = display_avatar(data.get("avatar_url"), colour)

    # ───────────────────────────────────────── profile → coloured field list ──
    elements = [
        {"label": colour.paint(colour.light_blue, "Username:"),     "value": data.get("login")},
        {"label": colour.paint(colour.yellow,     "Name:"),         "value": data.get("name") or "N/A"},
        {"label": colour.paint(colour.green,      "Bio:"),          "value": data.get("bio") or "N/A"},
        {"label": colour.paint(colour.red,        "Location:"),     "value": data.get("location") or "Not Provided"},
        {"label": colour.paint(colour.light_red,  "Public Repos:"), "value": data.get("public_repos")},
        {"label": colour.paint(colour.blue,       "Followers:"),    "value": data.get("followers")},
        {"label": colour.paint(colour.light_blue, "Following:"),    "value": data.get("following")},
        {"label": colour.paint(colour.yellow,     "Created:"),      "value": (data.get("created_at") or "")[:10]},
        {"label": colour.paint(colour.green,      "Profile URL:"),  "value": data.get("html_url")},
    ]

    # ─────────────────────────────── tidy text block (remove \n + wrap) ──
    info_lines = []
    WRAP   = 50                           # characters per line in the right column
    for item in elements:
        raw_val = str(item["value"]).replace("\n", " ")
        wrapped = textwrap.wrap(raw_val, WRAP) or [""]
        # first wrapped line with label
        info_lines.append(f"{item['label']} {wrapped[0]}")
        # further wrapped lines indented to align
        indent = " " * (len(item["label"]) + 1)
        for w in wrapped[1:]:
            info_lines.append(f"{indent}{w}")

    # ─────────────────────────────── side-by-side output ─────────────────
    AVATAR_WIDTH = 36                     # 18 “██” = 36 visible chars
    BLANK_AVATAR = " " * AVATAR_WIDTH
    SEP          = " | "

    max_rows = max(len(avatar_rows), len(info_lines))
    for i in range(max_rows):
        left  = avatar_rows[i] if i < len(avatar_rows) else BLANK_AVATAR
        right = info_lines[i]  if i < len(info_lines)  else ""
        print(f"{left}{SEP}{right}")

    print()                               # final new-line for neat prompt return


if __name__ == "__main__":
    main()