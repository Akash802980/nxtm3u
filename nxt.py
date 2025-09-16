import requests
import re
from urllib.parse import urlparse, parse_qs

# Sources
json_url = "https://ainonereborn.fun/jstrweb2/index.php"
backup_url = "https://game.denver1769.fun/Jtv/VPifZa/Jtv.mpd?id=143"
zee_m3u_url = "https://raw.githubusercontent.com/alex8875/m3u/refs/heads/main/z5.m3u"

# Playlist file
m3u_file = "backend.m3u"

def normalize_jio_token(raw):
    if not raw:
        return None
    raw = raw.strip()
    if raw.startswith("__hdnea__="):
        return raw
    return "__hdnea__=" + raw

def get_jio_token_from_json():
    try:
        data = requests.get(json_url, timeout=5).json()
        raw = data[0]["token"]
        return normalize_jio_token(raw)
    except Exception as e:
        print("⚠️ Jio JSON method failed:", e)
        return None

def get_jio_token_from_redirect():
    try:
        headers = {"User-Agent": "Denver1769"}
        resp = requests.get(backup_url, headers=headers, allow_redirects=True, timeout=5)
        final_url = resp.url
        parsed = urlparse(final_url)
        query_params = parse_qs(parsed.query)
        raw = query_params.get("__hdnea__", [""])[0]
        return normalize_jio_token(raw)
    except Exception as e:
        print("⚠️ Jio Redirect method failed:", e)
        return None

def get_zee_token():
    try:
        resp = requests.get(zee_m3u_url, timeout=5)
        resp.raise_for_status()
        text = resp.text
        # Find first occurrence of "?hdntl=" in the file, extract until a whitespace or line break
        match = re.search(r"\?hdntl=[^\s\"']+", text)
        if match:
            token_part = match.group(0).lstrip("?")  # e.g. "hdntl=exp=...~acl=...~hmac=..."
            return token_part
        else:
            print("⚠️ No hdntl token found in Zee m3u source.")
            return None
    except Exception as e:
        print("⚠️ Zee token fetch failed:", e)
        return None

def update_playlist(jio_token, zee_token):
    with open(m3u_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove old tokens
    content = re.sub(r"\?__hdnea__=[^\s\"]+", "", content)
    content = re.sub(r"\?hdntl=[^\s\"]+", "", content)

    # Add new Jio token
    if jio_token:
        content = re.sub(
            r"(https://jiotvmblive\.cdn\.jio\.com[^\s\"']+?\.mpd)",
            rf"\1?{jio_token}",
            content
        )

    # Add new Zee token
    if zee_token:
        content = re.sub(
            r"(https://z5ak-cmaflive\.zee5\.com[^\s\"']+?\.m3u8)",
            rf"\1?{zee_token}",
            content
        )

    with open(m3u_file, "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Playlist updated.")
    if jio_token:
        print("   Jio token:", jio_token)
    if zee_token:
        print("   Zee token:", zee_token)

def main():
    # Fetch tokens
    jio_token = get_jio_token_from_json() or get_jio_token_from_redirect()
    if not jio_token:
        raise Exception("❌ Could not fetch Jio token")

    zee_token = get_zee_token()
    if not zee_token:
        raise Exception("❌ Could not fetch Zee token")

    # Update playlist
    update_playlist(jio_token, zee_token)

if __name__ == "__main__":
    main()
