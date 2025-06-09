#!/usr/bin/python3

import requests
import sys
import os
from PIL import Image
import io

if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <your-github-username>")
    sys.exit(1)

class Color:
    def __init__(self):
        # Windows Command Prompt ANSI color codes
        self.red = "\033[91m"
        self.green = "\033[92m"
        self.yellow = "\033[93m"
        self.light_blue = "\033[94m"
        self.light_red = "\033[95m"
        self.blue = "\033[96m"
        self.reset = "\033[0m"
        
    def color(self, color_name, text):
        return f"{color_name}{text}{self.reset}"

def display_avatar(avatar_url):
    """Download and display avatar image (Windows compatible)"""
    try:
        # Download the image
        response = requests.get(avatar_url)
        if response.ok:
            # Try to display using PIL (if available)
            try:
                img = Image.open(io.BytesIO(response.content))
                # Resize for terminal display
                img.thumbnail((80, 80))
                
                # Try to display in Windows Terminal or compatible terminal
                # This works in Windows Terminal, PowerShell 7, or WSL
                print(f"Avatar URL: {avatar_url}")
                print("(Avatar image downloaded - view at URL above)")
                
            except ImportError:
                print(f"Avatar URL: {avatar_url}")
                print("(Install Pillow with 'pip install Pillow' for better image handling)")
                
    except Exception as e:
        print(f"Could not fetch avatar: {e}")

def enable_ansi_colors():
    """Enable ANSI colors in Windows Command Prompt"""
    if os.name == 'nt':  # Windows
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except:
            pass

# Enable colors for Windows
enable_ansi_colors()

color = Color()
indent = " " * 22
username = sys.argv[1]
github_url = f"{username}@github.com"
url = f"https://api.github.com/users/{username}"

print(f"Fetching GitHub profile for: {username}")
print("=" * 50)

response = requests.get(url)

if not response.ok:
    print(f"{color.red}Error: {response.status_code}{color.reset}")
    if response.status_code == 404:
        print(f"{color.red}User '{username}' not found on GitHub{color.reset}")
    sys.exit(1)

data = response.json()

# Display avatar
if data.get('avatar_url'):
    display_avatar(data.get('avatar_url'))

elements = [
    {"text": color.color(color.light_blue, "Username:"), "value": data.get('login')},
    {"text": color.color(color.yellow, "Name:"), "value": data.get('name', 'N/A') or 'N/A'},
    {"text": color.color(color.green, "Bio:"), "value": data.get('bio', 'N/A') or 'N/A'},
    {"text": color.color(color.red, "Location:"), "value": data.get('location', 'Not Provided') or 'Not Provided'},
    {"text": color.color(color.light_red, "Public Repos:"), "value": data.get('public_repos')},
    {"text": color.color(color.blue, "Followers:"), "value": data.get('followers')},
    {"text": color.color(color.light_blue, "Following:"), "value": data.get('following')},
    {"text": color.color(color.yellow, "Created:"), "value": data.get('created_at', 'N/A')[:10] if data.get('created_at') else 'N/A'},
    {"text": color.color(color.green, "Profile URL:"), "value": data.get('html_url')},
]

print(f"\n{indent} {github_url}")
print(f"{indent} {'-' * len(github_url)}")

for element in elements:
    print(f"{indent} {element['text']} {element['value']}")

print("\n" + "=" * 50)
print(f"{color.green}GitHub profile fetch completed!{color.reset}")
