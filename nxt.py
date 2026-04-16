import requests
import os
from datetime import datetime

API_URL = "https://host.cloudplay.me/app/icc/jo.php"
BACKUP_M3U = "https://joker-verse.vercel.app/jokertv/playlist.m3u?uid=1045595420&pass=169ae613&vod=true"
M3U_FILE = "Aki.m3u"

HOTSTAR_DOMAINS = ["jcevents.hotstar.com", "livetv.hotstar.com"]



def build_header(headers, ua):
    return (
        f'Cookie="{headers.get("Cookie","")}"'
        f'&User-Agent="{ua}"'
        f'&Origin="{headers.get("Origin","")}"'
        f'&Referer="{headers.get("Referer","")}"'
    )


# 🔹 API
def fetch_from_api():
    print("Trying API...")
    try:
        res = requests.get(API_URL, timeout=10)
        data = res.json()

        for ch in data:
            url = ch.get("m3u8_url", "")
            if any(d in url for d in HOTSTAR_DOMAINS):
                return build_header(ch.get("headers", {}), ch.get("user_agent", ""))

    except Exception as e:
        print("API Failed ❌", e)

    return None


# 🔹 BACKUP
def fetch_from_backup():
    print("Trying Backup M3U...")

    headers = {
        "User-Agent": "TiviMate/5.1.0 (Android 13)"
    }

    try:
        res = requests.get(BACKUP_M3U, headers=headers, timeout=15)
        lines = res.text.splitlines()

        for line in lines:
            if any(d in line for d in HOTSTAR_DOMAINS) and "|" in line:
                print("Backup cookie found ✅")
                return line.split("|", 1)[1].strip()

    except Exception as e:
        print("Backup Failed ❌", e)

    return None


# 🔹 UPDATE FILE
def update_all_links(header_str):
    print("Updating Hotstar links...")

    with open(M3U_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    domain_count = {d: 0 for d in HOTSTAR_DOMAINS}

    for line in lines:
        if any(d in line for d in HOTSTAR_DOMAINS):
            base_url = line.split("|")[0].strip()
            new_line = f"{base_url}|{header_str}\n"

            for d in HOTSTAR_DOMAINS:
                if d in line:
                    domain_count[d] += 1

            new_lines.append(new_line)
        else:
            new_lines.append(line)

    # 🔥 FORCE CHANGE (important)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_lines.insert(0, f"#EXTM3U\n# Updated at {timestamp}\n")
    new_lines.append(f"\n# end update {timestamp}\n")

    with open(M3U_FILE, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print("\n📊 Update Summary:")
    for d, count in domain_count.items():
        print(f"{d} → {count} links updated")


# 🔹 GIT PUSH
def git_push():
    print("\n🔄 Pushing to GitHub...")

    os.system("git add .")

    status = os.popen("git status --porcelain").read().strip()

    if not status:
        print("⚠️ No changes to commit")
        return

    msg = f"Auto update {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    os.system(f'git commit -m "{msg}"')

    os.system("git push origin main")

    print("🚀 GitHub Updated Successfully")


# 🔹 MAIN
def main():
    # 🔥 STEP 1: sync first
    os.system("git fetch origin")
    os.system("git reset --hard origin/main")

    header_str = fetch_from_api()

    if not header_str:
        print("Switching to backup...")
        header_str = fetch_from_backup()

    if not header_str:
        print("No valid cookie found ❌")
        return

    # 🔥 STEP 2: update file
    update_all_links(header_str)

    # 🔥 STEP 3: push
    git_push()

    print("\n✅ All done!")


if __name__ == "__main__":
    main()
