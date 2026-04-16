import requests
import re
import time
import shutil
from pathlib import Path

# ---------------- CONFIG ----------------
API_URL = "https://host.cloudplay.me/app/icc/jo.php"
BACKUP_URL = "https://joker-verse.vercel.app/jokertv/playlist.m3u?uid=1045595420&pass=169ae613&vod=true"

AK_FILE = "ak.m3u"
BACKUP_SUFFIX = ".bak"

HEADERS = {
    "User-Agent": "TiviMate/5.1.0 (Android 13)",
    "Accept-Encoding": "gzip",
    "Connection": "keep-alive"
}

RETRIES = 5
TIMEOUT = 30
# ---------------------------------------


# 🔹 DOWNLOAD WITH RETRY
def download_source(url, headers, retries=RETRIES, timeout=TIMEOUT):
    for attempt in range(1, retries + 1):
        try:
            print(f"[Download] Attempt {attempt} → {url}")
            r = requests.get(url, headers=headers, timeout=timeout)
            r.raise_for_status()
            return r.text
        except Exception as e:
            print(f"[Error] {e}, retrying...")
            time.sleep(3)

    raise RuntimeError(f"Failed to download: {url}")


# 🔹 FETCH FROM API (PRIMARY)
def fetch_from_api():
    print("[API] Trying primary source...")
    try:
        r = requests.get(API_URL, timeout=10)
        data = r.json()

        for ch in data:
            url = ch.get("m3u8_url", "")
            if "hotstar.com" in url:
                headers = ch.get("headers", {})
                ua = ch.get("user_agent", "")

                header_str = (
                    f'Cookie="{headers.get("Cookie","")}"'
                    f'&User-Agent="{ua}"'
                    f'&Origin="{headers.get("Origin","")}"'
                    f'&Referer="{headers.get("Referer","")}"'
                )

                print("[API] Cookie fetched ✅")
                return header_str

    except Exception as e:
        print("[API] Failed ❌", e)

    return None


# 🔹 EXTRACT TOKEN (hdntl)
def extract_token(source_text, base_url=None):
    if base_url:
        for m in re.finditer(re.escape(base_url), source_text):
            start = max(0, m.start() - 300)
            end = m.end() + 1500
            snippet = source_text[start:end]

            tok = re.search(r'hdntl=[^"&\s\|]+', snippet)
            if tok:
                return tok.group(0)

    # fallback
    tok = re.search(r'hdntl=[^"&\s\|]+', source_text)
    if tok:
        return tok.group(0)

    return None


# 🔹 UPDATE M3U FILE
def update_ak_m3u(ak_file, header_str=None, source_text=None):
    p = Path(ak_file)

    if not p.exists():
        raise FileNotFoundError(f"{ak_file} not found")

    # backup
    backup_path = p.with_suffix(p.suffix + BACKUP_SUFFIX)
    shutil.copy2(p, backup_path)
    print(f"[Backup] Saved: {backup_path}")

    lines = p.read_text(encoding="utf-8").splitlines(keepends=True)

    updated_lines = []
    total = 0
    updated = 0

    for line in lines:
        stripped = line.strip()

        if stripped.lower().startswith("http"):
            total += 1

            # base URL extract
            q_idx = len(stripped)
            for d in ['?', '|']:
                i = stripped.find(d)
                if i != -1:
                    q_idx = min(q_idx, i)

            base = stripped[:q_idx]

            # 🔹 METHOD 1: header replace (API)
            if header_str and "hotstar.com" in base:
                new_line = f"{base}|{header_str}\n"
                updated_lines.append(new_line)
                updated += 1
                continue

            # 🔹 METHOD 2: token replace (backup)
            if source_text and "hotstar.com" in base:
                token = extract_token(source_text, base)
                if token:
                    new_line = f"{base}?{token}\n"
                    updated_lines.append(new_line)
                    updated += 1
                    continue

        updated_lines.append(line)

    p.write_text("".join(updated_lines), encoding="utf-8")

    print(f"[Done] Total: {total}, Updated: {updated}")


# 🔹 MAIN
if __name__ == "__main__":

    print("==== START ====")

    # 1️⃣ Try API
    header_str = fetch_from_api()

    if header_str:
        print("[Mode] Using API headers")
        update_ak_m3u(AK_FILE, header_str=header_str)

    else:
        print("[Mode] API failed → using Backup")

        # 2️⃣ Backup download
        src_text = download_source(BACKUP_URL, HEADERS)

        # 3️⃣ Update using tokens
        update_ak_m3u(AK_FILE, source_text=src_text)

    print("✅ Finished")
