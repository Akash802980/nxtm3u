import re
import requests

# --- CONFIG ---
M3U_FILE = "Aki.m3u"  # Apni M3U file ka naam yahan likh
REMOTE_URL = "https://raw.githubusercontent.com/alex8875/m3u/refs/heads/main/jcinema.m3u"

def extract_cookie_from_remote(url):
    print(f"[+] Fetching cookie from: {url}")
    response = requests.get(url, timeout=10)
    data = response.text

    # Find cookie from EXTHTTP line
    match = re.search(r'"cookie"\s*:\s*"([^"]+)"', data)
    if not match:
        raise ValueError("❌ No cookie found in remote file!")
    
    cookie_value = match.group(1)
    print(f"[✓] Cookie fetched: {cookie_value[:70]}...")
    return cookie_value

def update_hotstar_cookies(file_path, new_cookie):
    print(f"[+] Updating only hotstar.com URLs in {file_path}...")

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    updated_lines = []
    for i in range(len(lines)):
        line = lines[i]
        
        # Check if line contains a hotstar.com URL and has a Cookie field
        if "hotstar.com" in line and 'Cookie="' in line:
            new_line = re.sub(r'Cookie="[^"]+"', f'Cookie="{new_cookie}"', line)
            updated_lines.append(new_line)
        else:
            updated_lines.append(line)

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(updated_lines)

    print(f"[✓] Updated all hotstar.com links with new cookie!")

if __name__ == "__main__":
    try:
        new_cookie = extract_cookie_from_remote(REMOTE_URL)
        update_hotstar_cookies(M3U_FILE, new_cookie)
    except Exception as e:
        print(f"[!] Error: {e}")
