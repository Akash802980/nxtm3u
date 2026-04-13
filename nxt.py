import requests
import re

# ===== SETTINGS =====
API_URL = "https://host.cloudplay.me/app/icc/hstr.php"
M3U_FILE = "Aki.m3u"
OUTPUT_FILE = "updated_playlist.m3u"

import requests

API_URL = "https://host.cloudplay.me/a/jo.php"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json",
    "Referer": "https://host.cloudplay.me/"
}

print("Fetching API data...")

res = requests.get(API_URL, headers=headers)

# DEBUG (bahut important)
print("Status Code:", res.status_code)

if res.status_code != 200:
    print("API request failed")
    exit()

# Check response content
if not res.text.strip():
    print("Empty response from API")
    exit()

# Try JSON safely
try:
    data = res.json()
except Exception as e:
    print("JSON Error:", e)
    print("Response was:\n", res.text[:500])  # first 500 chars
    exit()

print("API Loaded Successfully")
# ===== CREATE MAP (name -> headers/url) =====
channel_map = {}

for ch in data:
    if "jcevents.hotstar.com" in ch.get("m3u8_url", ""):
        name = ch.get("name").strip().lower()
        channel_map[name] = ch

print(f"Found {len(channel_map)} Hotstar channels")

# ===== READ M3U =====
with open(M3U_FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

updated_lines = []
i = 0

while i < len(lines):
    line = lines[i]

    # EXTINF line
    if line.startswith("#EXTINF"):
        name_match = re.search(r",\s*(.+)", line)
        if name_match:
            name = name_match.group(1).strip().lower()
        else:
            updated_lines.append(line)
            i += 1
            continue

        updated_lines.append(line)

        # Next line is URL
        if i + 1 < len(lines):
            url_line = lines[i + 1]

            # Check if hotstar link
            if "jcevents.hotstar.com" in url_line and name in channel_map:
                ch = channel_map[name]

                new_url = ch["m3u8_url"]
                headers = ch.get("headers", {})
                ua = ch.get("user_agent", "")

                cookie = headers.get("Cookie", "")
                origin = headers.get("Origin", "")
                referer = headers.get("Referer", "")

                # Build new line
                new_line = f'{new_url}|Cookie="{cookie}"&User-Agent="{ua}"&Origin="{origin}"&Referer="{referer}"\n'

                updated_lines.append(new_line)
                print(f"Updated: {name}")

            else:
                updated_lines.append(url_line)

            i += 2
            continue

    updated_lines.append(line)
    i += 1

# ===== SAVE FILE =====
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.writelines(updated_lines)

print("Done! Updated playlist saved.")
