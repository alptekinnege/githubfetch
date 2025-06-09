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
    """Download and display avatar as true-color ASCII art"""
    try:
        response = requests.get(avatar_url)
        if response.ok:
            try:
                img = Image.open(io.BytesIO(response.content))
                # Convert to RGB to ensure we have color data
                img = img.convert('RGB')
                # Make it truly square
                img = img.resize((18, 18))  # Perfect square
                
                ascii_art = []
                for y in range(img.height):
                    row = []
                    for x in range(img.width):
                        r, g, b = img.getpixel((x, y))
                        
                        # Use true color ANSI codes for accurate colors
                        # Format: \033[38;2;r;g;bm for foreground color
                        true_color = f"\033[38;2;{r};{g};{b}m"
                        
                        # Use block character to represent the pixel
                        colored_block = f"{true_color}██{color.reset}"
                        row.append(colored_block)
                    ascii_art.append(''.join(row))
                
                return ascii_art
                
            except ImportError:
                pass
                
    except Exception:
        pass
    
    return []

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

response = requests.get(url)

if not response.ok:
    print(f"{color.red}Error: {response.status_code}{color.reset}")
    if response.status_code == 404:
        print(f"{color.red}User '{username}' not found on GitHub{color.reset}")
    sys.exit(1)

data = response.json()

# Display avatar
avatar_art = []
if data.get('avatar_url'):
    avatar_art = display_avatar(data.get('avatar_url'))

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

print(f"\n{github_url}")
print(f"{'-' * len(github_url)}")

# Display info with avatar on the side
for i, element in enumerate(elements):
    info_line = f"{element['text']} {element['value']}"
    if i < len(avatar_art):
        # Show avatar art alongside info
        print(f"{avatar_art[i]}  {info_line}")
    else:
        # Show just info when avatar art is done
        print(f"{' ' * 38}{info_line}")

# Show remaining avatar art if any
if len(avatar_art) > len(elements):
    for i in range(len(elements), len(avatar_art)):
        print(avatar_art[i])

print("\n")