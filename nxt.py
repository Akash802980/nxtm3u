import requests
import re
from urllib.parse import urlparse, parse_qs

# Sources
json_url = "https://allinonereborn.fun/jstrweb2/index.php"
backup_url = "https://game.denver1769.fun/Jtv/VPifZa/Jtv.mpd?id=143"

# Playlist file
m3u_file = "jio all1.m3u"

def get_token_from_json():
    try:
        data = requests.get(json_url, timeout=5).json()
        raw = data[0]["token"]  # e.g. st=...~exp=...~hmac=...
        return f"__hdnea__={raw}"
    except Exception as e:
        print("⚠️ JSON method failed:", e)
        return None

def get_token_from_redirect():
    try:
        headers = {"User-Agent": "Denver1769"}
        resp = requests.get(backup_url, headers=headers, allow_redirects=True, timeout=5)
        final_url = resp.url
        parsed = urlparse(final_url)
        query_params = parse_qs(parsed.query)
        token_val = query_params.get("__hdnea__", [""])[0]
        if token_val:
            return f"__hdnea__={token_val}"
        return None
    except Exception as e:
        print("⚠️ Redirect method failed:", e)
        return None

# 1. Try JSON first
new_token = get_token_from_json()

# 2. If failed, fallback to redirect
if not new_token:
    print("➡️ Falling back to redirect method...")
    new_token = get_token_from_redirect()

if not new_token:
    raise Exception("❌ Could not fetch token from either method")

# --- Update Playlist ---
with open(m3u_file, "r", encoding="utf-8") as f:
    content = f.read()

# Remove old token
content = re.sub(r"\?__hdnea__=.*", "", content)

# Add new token to .mpd URLs
content = re.sub(
    r"(https://jiotvmblive\.cdn\.jio\.com[^\s]+?\.mpd)",
    rf"\1?{new_token}",
    content
)

# Replace in #EXTHTTP
content = re.sub(
    r'(#EXTHTTP:{"cookie":").*?"}',
    rf'\1{new_token}"',
    content
)

# Save back
with open(m3u_file, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Playlist updated with token:", new_token)
