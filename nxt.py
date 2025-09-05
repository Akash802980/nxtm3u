import requests
import re
from urllib.parse import urlparse, parse_qs

# Sources
json_url = "https://allinonereborn.fun/jstrweb2/index.php"
redirect_url = "https://game.denver1769.fun/Jtv/VPifZa/Jtv.mpd?id=143"
m3u_file = "backend.m3u"

def get_token_from_json():
    try:
        data = requests.get(json_url, timeout=5).json()
        return data[0]["token"]
    except Exception as e:
        print("⚠️ JSON source failed:", e)
        return None

def get_token_from_redirect():
    headers = {"User-Agent": "Denver1769"}
    resp = requests.get(redirect_url, headers=headers, allow_redirects=True, timeout=5)
    final_url = resp.url
    parsed = urlparse(final_url)
    query_params = parse_qs(parsed.query)
    return query_params.get("__hdnea__", [""])[0]

# 1. Try JSON first
token = get_token_from_json()

# 2. If JSON fails, fallback to redirect method
if not token:
    print("➡️ Falling back to redirect method...")
    token = get_token_from_redirect()

if not token:
    raise Exception("❌ Could not retrieve token from any source")

# Update playlist
with open(m3u_file, "r", encoding="utf-8") as f:
    content = f.read()

# Remove old token
content = re.sub(r"\?__hdnea__=.*", "", content)

# Add new token to .mpd URLs
content = re.sub(
    r"(https://jiotvmblive\.cdn\.jio\.com[^\s]+?\.mpd)",
    rf"\1?__hdnea__={token}",
    content
)

# Replace token in #EXTHTTP
content = re.sub(
    r'(#EXTHTTP:{"cookie":")__hdnea__=.*?"}',
    rf'\1__hdnea__={token}"',
    content
)

# Save back
with open(m3u_file, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Playlist updated with token:", token)
