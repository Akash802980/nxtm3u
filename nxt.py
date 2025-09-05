import cloudscraper
import re
import json

json_url = "https://allinonereborn.fun/jstrweb2/index.php"
m3u_file = "backend.m3u"

# cloudscraper with browser emulation
scraper = cloudscraper.create_scraper(
    browser={"browser": "chrome", "platform": "windows", "mobile": False}
)

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/116.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
    "Referer": "https://allinonereborn.fun/",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}

resp = scraper.get(json_url, headers=headers)

try:
    data = resp.json()
    new_token = data[0]["token"]
except Exception as e:
    print("❌ JSON parse error:", e)
    print("Status code:", resp.status_code)
    print("Response text (first 300 chars):", resp.text[:300])
    raise SystemExit(1)

with open(m3u_file, "r", encoding="utf-8") as f:
    content = f.read()

# remove old token from mpd URLs
content = re.sub(r"\?__hdnea__=.*", "", content)

# add new token to mpd URLs
content = re.sub(
    r"(https://jiotvmblive\.cdn\.jio\.com[^\s]+?\.mpd)",
    rf"\1?{new_token}",
    content
)

# update token in #EXTHTTP cookie line
content = re.sub(
    r'(#EXTHTTP:{"cookie":")__hdnea__=.*?"}',
    rf'\1{new_token}"',
    content
)

with open(m3u_file, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Playlist updated with token:", new_token)
