#!/usr/bin/env python3
"""
gitcard.py  –  Show a GitHub user’s avatar + profile details + top-5 repos
"""
import os, sys, io, textwrap, requests
from PIL import Image

# ─────────────────────────────────────────── Colours ──────────────────────────
class Color:
    def __init__(self):
        self.red        = "\033[91m"
        self.green      = "\033[92m"
        self.yellow     = "\033[93m"
        self.light_blue = "\033[94m"
        self.light_red  = "\033[95m"
        self.blue       = "\033[96m"
        self.reset      = "\033[0m"

    def paint(self, code, text):       # helper to colourise text
        return f"{code}{text}{self.reset}"


# ───────────────────────────── Enable ANSI colours on Windows ────────────────
def enable_ansi_colors():
    if os.name == "nt":
        try:
            import ctypes
            k32  = ctypes.windll.kernel32
            k32.SetConsoleMode(k32.GetStdHandle(-11), 7)   # ENABLE_VIRTUAL_TERMINAL
        except Exception:
            pass


# ───────────────────────────────── Avatar → true-colour ASCII ────────────────
def fetch_avatar_rows(avatar_url: str, clr: Color, size: int = 18) -> list[str]:
    """Return list of strings, each row is a true-colour ASCII '██' block row."""
    try:
        resp = requests.get(avatar_url, timeout=10)
        resp.raise_for_status()
        img  = Image.open(io.BytesIO(resp.content)).convert("RGB").resize((size, size))
        rows = []
        for y in range(size):
            line = []
            for x in range(size):
                r, g, b = img.getpixel((x, y))
                line.append(f"\033[38;2;{r};{g};{b}m██{clr.reset}")
            rows.append("".join(line))
        return rows
    except Exception:
        return []


# ─────────────────────────────────────── MAIN ────────────────────────────────
def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(f"Usage: {sys.argv[0]} <github-user>")

    username = sys.argv[1]
    enable_ansi_colors()
    clr = Color()

    print(f"Fetching GitHub profile for: {username}")

    # 1) ───── profile data ────────────────────────────────────────────────────
    user_url = f"https://api.github.com/users/{username}"
    u_resp   = requests.get(user_url, timeout=10)

    if u_resp.status_code == 404:
        sys.exit(clr.paint(clr.red, f"Error: user '{username}' not found."))
    if not u_resp.ok:
        sys.exit(clr.paint(clr.red, f"GitHub API error: {u_resp.status_code}"))

    user = u_resp.json()
    avatar_rows = fetch_avatar_rows(user.get("avatar_url", ""), clr)

    # 2) ───── TOP-5 repositories by stars ─────────────────────────────────────
    repo_url = f"https://api.github.com/users/{username}/repos?per_page=100"
    r_resp   = requests.get(repo_url, timeout=10)
    repos    = r_resp.json() if r_resp.ok else []

    # sort by stars ↓ and keep max 5
    top_repos = sorted(repos, key=lambda r: r.get("stargazers_count", 0), reverse=True)[:5]

    # 3) ───── build text (label + value) list ─────────────────────────────────
    elements = [
        {"label": clr.paint(clr.light_blue, "Username:"),     "value": user.get("login")},
        {"label": clr.paint(clr.yellow,     "Name:"),         "value": user.get("name") or "N/A"},
        {"label": clr.paint(clr.green,      "Bio:"),          "value": user.get("bio")  or "N/A"},
        {"label": clr.paint(clr.red,        "Location:"),     "value": user.get("location") or "Not Provided"},
        {"label": clr.paint(clr.light_red,  "Public Repos:"), "value": user.get("public_repos")},
        {"label": clr.paint(clr.blue,       "Followers:"),    "value": user.get("followers")},
        {"label": clr.paint(clr.light_blue, "Following:"),    "value": user.get("following")},
        {"label": clr.paint(clr.yellow,     "Created:"),      "value": (user.get("created_at") or "")[:10]},
        {"label": clr.paint(clr.green,      "Profile URL:"),  "value": user.get("html_url")},
    ]

    # append repo section header
    if top_repos:
        elements.append({"label": clr.paint(clr.light_red, "Top Repos:"), "value": ""})
        for repo in top_repos:
            stars = repo.get("stargazers_count", 0)
            name  = repo.get("name")
            desc  = (repo.get("description") or "").splitlines()[0]      # first line only
            repo_line = f"⭐ {name} ({stars}) — {desc}" if desc else f"⭐ {name} ({stars})"
            elements.append({"label": " " * 11, "value": repo_line})     # 11 = len("Top Repos:")

    # 4) ───── wrap text → list of printable lines ────────────────────────────
    WRAP = 50
    info_lines = []
    for it in elements:
        raw = str(it["value"]).replace("\n", " ")
        wrapped = textwrap.wrap(raw, WRAP) or [""]
        info_lines.append(f"{it['label']} {wrapped[0]}".rstrip())
        indent = " " * (len(it["label"]) + 1)
        for w in wrapped[1:]:
            info_lines.append(f"{indent}{w}")

    # 5) ───── print side-by-side ─────────────────────────────────────────────
    AVATAR_W   = 36             # 18*2 "██"
    BLANK_AVTR = " " * AVATAR_W
    SEP        = " | "

    for i in range(max(len(avatar_rows), len(info_lines))):
        left  = avatar_rows[i] if i < len(avatar_rows) else BLANK_AVTR
        right = info_lines[i]  if i < len(info_lines)  else ""
        print(f"{left}{SEP}{right}")

    print()     # tidy prompt


if __name__ == "__main__":
    main()