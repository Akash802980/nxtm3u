import re
import requests

# --- CONFIG ---
M3U_FILE = "Aki.m3u"
HOTSTAR_REMOTE_URL = "https://raw.githubusercontent.com/alex8875/m3u/refs/heads/main/jcinema.m3u"

# Airtel SONY SAB cookie source
SONY_SAB_URL = "https://redcdn.online/airtel/live/126/med14-2/sony_sab/ndashd/sony_sab.mpd?uid=1045595420&pass=169ae613"
SONY_SAB_HEADERS = {
    "Host": "redcdn.online",
    "x-user-agent": "TiviMate/4.6.1 (Linux; Android 11)",
    "user-agent": "tv.accedo.airtel.wynk/1.97.1 (Linux;Android 13) ExoPlayerLib/2.19.1",
    "accept-encoding": "gzip"
}

# === GET LATEST HOTSTAR COOKIE ===
def extract_hotstar_cookie(url):
    print(f"[+] Fetching Hotstar cookie from: {url}")
    response = requests.get(url, timeout=10)
    data = response.text

    match = re.search(r'"cookie"\s*:\s*"([^"]+)"', data)
    if not match:
        raise ValueError("❌ No cookie found in Hotstar source file!")
    
    cookie_value = match.group(1)
    print(f"[✓] Hotstar cookie fetched: {cookie_value[:60]}...")
    return cookie_value


# === GET LATEST SONY SAB EDGE-CACHE-COOKIE ===
def fetch_sony_sab_cookie():
    print(f"[+] Fetching SONY SAB Edge-Cache-Cookie...")
    try:
        response = requests.get(SONY_SAB_URL, headers=SONY_SAB_HEADERS, timeout=10)
        set_cookie = response.headers.get("Set-Cookie")

        if set_cookie:
            match = re.search(r"(Edge-Cache-Cookie=[^;]+;)", set_cookie)
            if match:
                cookie_value = match.group(1)
                print(f"[✓] SONY SAB cookie fetched: {cookie_value}")
                return cookie_value
            else:
                print("⚠️ No Edge-Cache-Cookie found in Set-Cookie header.")
        else:
            print("⚠️ No Set-Cookie header found in response.")
    except Exception as e:
        print(f"[!] Error fetching SONY SAB cookie: {e}")
    return None


# === UPDATE M3U FILE ===
def update_m3u_file(file_path, hotstar_cookie, sony_cookie):
    print(f"[+] Updating {file_path}...")

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    updated_lines = []
    for line in lines:
        # 🔹 Hotstar update
        if "hotstar.com" in line and 'Cookie="' in line:
            line = re.sub(r'Cookie="[^"]+"', f'Cookie="{hotstar_cookie}"', line)

        # 🔹 SONY SAB Edge-Cache-Cookie update
        elif 'Edge-Cache-Cookie=' in line and sony_cookie:
            line = re.sub(
                r'Edge-Cache-Cookie=[^"]+',
                sony_cookie.strip(';'),  # remove trailing ;
                line
            )

        updated_lines.append(line)

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(updated_lines)

    print(f"[✓] All cookies updated successfully!")


if __name__ == "__main__":
    try:
        # Step 1: Fetch both cookies
        hotstar_cookie = extract_hotstar_cookie(HOTSTAR_REMOTE_URL)
        sony_cookie = fetch_sony_sab_cookie()

        # Step 2: Update M3U file
        update_m3u_file(M3U_FILE, hotstar_cookie, sony_cookie)
        print("\n🎉 M3U updated successfully with both Hotstar + Sony SAB cookies!")
    except Exception as e:
        print(f"[!] Error: {e}")
