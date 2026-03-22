# Github fetch

A neofetch-like program for GitHub profiles. Shows user avatar as true-color ASCII art alongside profile information and top repositories.

## Features
- True-color ASCII avatar display
- Profile information (name, bio, location, stats)
- Top 5 repositories sorted by stars
- Cross-platform support (Windows, Linux, macOS)

## Requirements
- Python 3.7+
- requests
- pillow

## Installation

```bash
git clone https://github.com/alptekinnege/githubfetch.git
cd githubfetch
pip install -r requirements.txt
```

## Usage
```bash
python githubfetch.py <username>
```

Example:
```bash
python githubfetch.py torvalds
```

## Example Output
![example image](screenshot.png)

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
