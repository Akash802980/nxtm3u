import requests
import re
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timezone, timedelta

# Sources
json_url = "https://allinonereborn.xyz/jstrweb2/jio.php"
backup_url = "https://game.denver1769.fun/Jtv/xVFuuG/Jtv.mpd?id=143"
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
        return normalize_jio_token(raw), data[0]["mpd"].split("/")[2]  # token + domain
    except Exception as e:
        print("⚠️ Jio JSON method failed:", e)
        return None, None

def get_jio_token_from_redirect():
    try:
        headers = {"User-Agent": "Denver1769"}
        resp = requests.get(backup_url, headers=headers, allow_redirects=True, timeout=5)
        final_url = resp.url
        parsed = urlparse(final_url)
        query_params = parse_qs(parsed.query)
        raw = query_params.get("__hdnea__", [""])[0]
        domain = parsed.netloc
        return normalize_jio_token(raw), domain
    except Exception as e:
        print("⚠️ Jio Redirect method failed:", e)
        return None, None

def get_zee_token():
    try:
        resp = requests.get(zee_m3u_url, timeout=5)
        resp.raise_for_status()
        text = resp.text
        match = re.search(r"\?hdntl=[^\s\"']+", text)
        if match:
            token_part = match.group(0).lstrip("?")
            return token_part
        else:
            print("⚠️ No hdntl token found in Zee m3u source.")
            return None
    except Exception as e:
        print("⚠️ Zee token fetch failed:", e)
        return None

def extract_old_tokens():
    """Extract old tokens from backend.m3u (for status line)."""
    try:
        with open(m3u_file, "r", encoding="utf-8") as f:
            content = f.read()
        jio_old = re.search(r"__hdnea__=[^\s\"']+", content)
        zee_old = re.search(r"hdntl=[^\s\"']+", content)
        return (jio_old.group(0) if jio_old else None,
                zee_old.group(0) if zee_old else None)
    except FileNotFoundError:
        return None, None

def extract_expiry_time(token):
    """Extract exp timestamp from token and convert to IST human time."""
    if not token:
        return None
    match = re.search(r"(?:exp|~exp)=(\d+)", token)
    if not match:
        return None
    try:
        ts = int(match.group(1))
        dt_utc = datetime.fromtimestamp(ts, tz=timezone.utc)
        # Convert to IST (UTC+5:30)
        ist = dt_utc + timedelta(hours=5, minutes=30)
        return ist.strftime("%Y-%m-%d %H:%M:%S IST")
    except Exception:
        return None

def update_backend_status(old_jio, new_jio, old_zee5, new_zee5):
    jio_exp = extract_expiry_time(new_jio)
    zee_exp = extract_expiry_time(new_zee5)

    status_line = f"# Jio Exp: {jio_exp or 'N/A'} | Zee5 Exp: {zee_exp or 'N/A'} | Updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"

    try:
        with open(m3u_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []

    if lines and (lines[0].startswith("# Jio Exp:") or lines[0].startswith("# Jio Token:")):
        lines[0] = status_line
    else:
        lines.insert(0, status_line)

    with open(m3u_file, "w", encoding="utf-8") as f:
        f.writelines(lines)

def update_playlist(jio_token, jio_domain, zee_token):
    with open(m3u_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove old tokens
    content = re.sub(r"\?__hdnea__=[^\s\"]+", "", content)
    content = re.sub(r"\?hdntl=[^\s\"]+", "", content)

    # Add new Jio token (with correct domain)
    if jio_token and jio_domain:
        content = re.sub(
            r"(https://)([^/]+)(/bpk-tv/[^\s\"']+?\.mpd)",
            rf"\1{jio_domain}\3?{jio_token}",
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

def main():
    old_jio, old_zee = extract_old_tokens()

    # Fetch Jio token
    jio_token, jio_domain = get_jio_token_from_json()
    if not jio_token:
        jio_token, jio_domain = get_jio_token_from_redirect()
    if not jio_token:
        raise Exception("❌ Could not fetch Jio token")

    # Fetch Zee token
    zee_token = get_zee_token()
    if not zee_token:
        raise Exception("❌ Could not fetch Zee token")

    # Update playlist
    update_playlist(jio_token, jio_domain, zee_token)

    # Update backend status line
    update_backend_status(old_jio, jio_token, old_zee, zee_token)

if __name__ == "__main__":
    main()
    
