#!/usr/bin/env python3
"""
GitHub Profile Card Generator
Kullanım: python gitcard.py <github-username>
"""

import sys
import os
import io
import textwrap
from datetime import datetime
import requests
from PIL import Image

# Windows için ANSI renk desteğini etkinleştir
if sys.platform == 'win32':
    os.system('color')

# ANSI renk kodları
class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BRIGHT_RED = '\033[31m'
    BRIGHT_BLUE = '\033[34m'

def rgb_to_ansi(r, g, b):
    """RGB değerlerini ANSI true-color koduna çevir"""
    return f'\033[38;2;{r};{g};{b}m'

def download_avatar(url, size=(18, 18)):
    """Avatar'ı indir ve boyutlandır"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        img = Image.open(io.BytesIO(response.content))
        img = img.convert('RGB')
        img = img.resize(size, Image.Resampling.LANCZOS)
        
        return img
    except Exception as e:
        print(f"{Colors.RED}Avatar indirilemedi: {e}{Colors.RESET}")
        return None

def image_to_ascii(img):
    """Resmi renkli ASCII art'a çevir"""
    if not img:
        return []
    
    ascii_lines = []
    width, height = img.size
    
    for y in range(height):
        line = ""
        for x in range(width):
            r, g, b = img.getpixel((x, y))
            color = rgb_to_ansi(r, g, b)
            line += f"{color}██{Colors.RESET}"
        ascii_lines.append(line)
    
    return ascii_lines

def fetch_github_data(username):
    """GitHub API'den kullanıcı verilerini çek"""
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'GitHub-Profile-Card-Generator'
    }
    
    try:
        # Kullanıcı bilgilerini çek
        user_response = requests.get(
            f'https://api.github.com/users/{username}',
            headers=headers,
            timeout=10
        )
        user_response.raise_for_status()
        user_data = user_response.json()
        
        # Repository'leri çek
        repos_response = requests.get(
            f'https://api.github.com/users/{username}/repos',
            headers=headers,
            params={'type': 'public', 'per_page': 100},
            timeout=10
        )
        repos_response.raise_for_status()
        repos_data = repos_response.json()
        
        return user_data, repos_data
    
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"{Colors.RED}Hata: '{username}' kullanıcısı bulunamadı!{Colors.RESET}")
        else:
            print(f"{Colors.RED}GitHub API hatası: {e}{Colors.RESET}")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print(f"{Colors.RED}Hata: İstek zaman aşımına uğradı!{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}Beklenmeyen hata: {e}{Colors.RESET}")
        sys.exit(1)

def format_date(date_string):
    """ISO formatındaki tarihi okunabilir formata çevir"""
    date = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
    return date.strftime('%d %B %Y')

def wrap_text(text, width=50):
    """Uzun metinleri belirtilen genişlikte sarmalama"""
    if not text:
        return []
    return textwrap.wrap(text, width=width)

def get_top_repos(repos, count=5):
    """En popüler repository'leri getir"""
    sorted_repos = sorted(repos, key=lambda x: x.get('stargazers_count', 0), reverse=True)
    return sorted_repos[:count]

def display_profile_card(username):
    """GitHub profil kartını oluştur ve göster"""
    # Verileri çek
    user_data, repos_data = fetch_github_data(username)
    
    # Avatar'ı indir ve ASCII'ye çevir
    avatar_url = user_data.get('avatar_url', '')
    avatar_img = download_avatar(avatar_url)
    avatar_lines = image_to_ascii(avatar_img)
    
    # Profil bilgilerini hazırla
    profile_lines = []
    
    # Username
    profile_lines.append(f"{Colors.CYAN}Username: {user_data.get('login', 'N/A')}{Colors.RESET}")
    
    # Name
    name = user_data.get('name', 'N/A')
    profile_lines.append(f"{Colors.YELLOW}Name: {name}{Colors.RESET}")
    
    # Bio
    bio = user_data.get('bio', 'N/A')
    if bio and bio != 'N/A':
        bio_lines = wrap_text(bio, 50)
        profile_lines.append(f"{Colors.GREEN}Bio: {bio_lines[0]}{Colors.RESET}")
        for line in bio_lines[1:]:
            profile_lines.append(f"{Colors.GREEN}     {line}{Colors.RESET}")
    else:
        profile_lines.append(f"{Colors.GREEN}Bio: N/A{Colors.RESET}")
    
    # Location
    location = user_data.get('location', 'N/A')
    profile_lines.append(f"{Colors.RED}Location: {location}{Colors.RESET}")
    
    # Stats
    profile_lines.append(f"{Colors.BRIGHT_RED}Public Repos: {user_data.get('public_repos', 0)}{Colors.RESET}")
    profile_lines.append(f"{Colors.BLUE}Followers: {user_data.get('followers', 0)}{Colors.RESET}")
    profile_lines.append(f"{Colors.CYAN}Following: {user_data.get('following', 0)}{Colors.RESET}")
    
    # Created date
    created_at = user_data.get('created_at', '')
    if created_at:
        formatted_date = format_date(created_at)
        profile_lines.append(f"{Colors.YELLOW}Created: {formatted_date}{Colors.RESET}")
    
    # Profile URL
    profile_lines.append(f"{Colors.GREEN}Profile: {user_data.get('html_url', 'N/A')}{Colors.RESET}")
    
    # Boş satır
    profile_lines.append("")
    
    # Top 5 Repository
    profile_lines.append(f"{Colors.MAGENTA}Top Repositories:{Colors.RESET}")
    top_repos = get_top_repos(repos_data, 5)
    
    for repo in top_repos:
        stars = repo.get('stargazers_count', 0)
        name = repo.get('name', 'N/A')
        description = repo.get('description', 'No description')
        
        if description and len(description) > 40:
            description = description[:37] + "..."
        
        profile_lines.append(f"{Colors.YELLOW}⭐ {name} ({stars}){Colors.RESET} — {description}")
    
    # Avatar ve profil bilgilerini yan yana göster
    print("\n" + "="*80)
    print(f"{Colors.CYAN}GitHub Profile Card - @{username}{Colors.RESET}")
    print("="*80 + "\n")
    
    # Her satırı yan yana yazdır
    max_lines = max(len(avatar_lines), len(profile_lines))
    
    for i in range(max_lines):
        # Avatar satırı
        if i < len(avatar_lines):
            avatar_line = avatar_lines[i]
        else:
            avatar_line = " " * 36  # 18 * 2 karakter genişlik
        
        # Profil satırı
        if i < len(profile_lines):
            profile_line = profile_lines[i]
        else:
            profile_line = ""
        
        print(f"{avatar_line} | {profile_line}")
    
    print("\n" + "="*80 + "\n")

def main():
    """Ana fonksiyon"""
    if len(sys.argv) != 2:
        print(f"{Colors.RED}Kullanım: python {sys.argv[0]} <github-username>{Colors.RESET}")
        sys.exit(1)
    
    username = sys.argv[1]
    display_profile_card(username)

if __name__ == "__main__":
    main()