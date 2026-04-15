import requests
import re

API_URL = "https://host.cloudplay.me/app/icc/hstr.php"
M3U_FILE = "Aki.m3u"

def fetch_cookie_data():
    print("Fetching API data...")
    res = requests.get(API_URL)
    data = res.json()

    # kisi bhi ek valid hotstar entry se cookie uthao
    for ch in data:
        url = ch.get("m3u8_url", "")
        if "jcevents.hotstar.com" in url:
            headers = ch.get("headers", {})
            ua = ch.get("user_agent", "")

            header_str = f'Cookie="{headers.get("Cookie","")}"'
            header_str += f'&User-Agent="{ua}"'
            header_str += f'&Origin="{headers.get("Origin","")}"'
            header_str += f'&Referer="{headers.get("Referer","")}"'

            return header_str

    return None

def update_all_hotstar_links(header_str):
    print("Updating all Hotstar links...")

    with open(M3U_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []

    for line in lines:
        if "jcevents.hotstar.com" in line:
            base_url = line.split("|")[0].strip()
            new_line = f"{base_url}|{header_str}\n"
            print(f"Updated: {base_url}")
            new_lines.append(new_line)
        else:
            new_lines.append(line)

    with open(M3U_FILE, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

def main():
    header_str = fetch_cookie_data()

    if not header_str:
        print("No valid cookie found ❌")
        return

    update_all_hotstar_links(header_str)
    print("All links updated ✅")

if __name__ == "__main__":
    main()
