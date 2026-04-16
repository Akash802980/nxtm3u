import requests
import os
from datetime import datetime
 
API_URL = "https://host.cloudplay.me/app/icc/jo.php"
BACKUP_M3U = "https://joker-verse.vercel.app/jokertv/playlist.m3u?uid=1045595420&pass=169ae613&vod=true"
M3U_FILE = "Aki.m3u"
HOTSTAR_DOMAINS = ["jcevents.hotstar.com", "livetv.hotstar.com"]


def build_header(headers, ua):
    """API से मिले डेटा को हेडर स्ट्रिंग में बदलना"""
    return (
        f'Cookie="{headers.get("Cookie","")}"'
        f'&User-Agent="{ua}"'
        f'&Origin="{headers.get("Origin","")}"'
        f'&Referer="{headers.get("Referer","")}"'
    )


def fetch_from_api():
    """API सोर्स से कुकी निकालना"""
    print("Trying API...")
    try:
        headers = {
            "User-Agent": "Hotstar;in.startv.hotstar/25.01.27.5.3788 (Android/13)",
            "Referer": "https://www.hotstar.com/",
            "Origin": "https://www.hotstar.com"
        }

        res = requests.get(API_URL, headers=headers, timeout=10)
        data = res.json()

        for ch in data:
            url = ch.get("m3u8_url", "")
            if any(d in url for d in HOTSTAR_DOMAINS):
                print("API cookie found ✅")
                return build_header(ch.get("headers", {}), ch.get("user_agent", ""))

    except Exception as e:
        print("API Failed ❌", e)

    return None


def fetch_from_backup():
    """बैकअप M3U से कुकी निकालना"""
    print("Trying Backup M3U...")
    headers = {"User-Agent": "TiviMate/5.1.0 (Android 13)"}

    try:
        res = requests.get(BACKUP_M3U, headers=headers, timeout=15)

        if res.status_code != 200:
            print("Backup HTTP Error:", res.status_code)
            return None

        text = res.text
        lines = text.splitlines()

        for line in lines:
            if any(d in line for d in HOTSTAR_DOMAINS) and "|" in line:
                header_part = line.split("|", 1)[1].strip()

                if "Cookie=" in header_part:
                    print("Backup cookie found ✅")
                    return header_part

        print("No valid header in backup ❌")

    except Exception as e:
        print("Backup Failed ❌", e)

    return None


def update_all_links(header_str):
    """M3U फ़ाइल के अंदर लिंक्स को अपडेट करना"""
    print("Updating Hotstar links...")

    if not os.path.exists(M3U_FILE):
        print(f"Error: {M3U_FILE} not found!")
        return

    with open(M3U_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    domain_count = {d: 0 for d in HOTSTAR_DOMAINS}

    for line in lines:
        if any(d in line for d in HOTSTAR_DOMAINS):
            # पुराने हेडर को हटाकर नया जोड़ना
            base_url = line.split("|")[0].strip()
            new_line = f"{base_url}|{header_str}\n"

            for d in HOTSTAR_DOMAINS:
                if d in line:
                    domain_count[d] += 1
            new_lines.append(new_line)
        else:
            new_lines.append(line)

    # फ़ाइल की शुरुआत में अपडेट का समय डालना
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_lines.insert(0, f"#EXTM3U\n# Updated at {timestamp}\n")

    with open(M3U_FILE, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print("\n📊 Update Summary:")
    for d, count in domain_count.items():
        print(f"{d} → {count} links updated")


# 🔹 GIT PUSH (FORCEFULLY UPDATED 🔥)
def git_push():
    print("\n🔄 Syncing GitHub Forcefully...")

    # 1. पहले अपनी पहचान सेट करें (अगर सर्वर पर एरर आ रहा हो)
    os.system('git config user.name "Auto Bot"')
    os.system('git config user.email "bot@example.com"')

    # 2. पुरानी फाइलों को अपडेट करें
    os.system("git add .")

    # 3. चेक करें कि कुछ बदलने के लिए है या नहीं
    status = os.popen("git status --porcelain").read().strip()
    if not status:
        print("⚠️ No changes detected in the file.")
        # कभी-कभी बिना बदलाव के भी पुश करने के लिए हम आगे बढ़ सकते हैं
    
    # 4. कमिट करें
    msg = f"Auto update {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    os.system(f'git commit -m "{msg}"')

    # 5. FORCE PUSH (यह पुराने इतिहास को ओवरराइट कर देगा और फाइल अपडेट कर देगा)
    # '-f' का मतलब है Force
    print("🚀 Pushing changes to GitHub...")
    result = os.system("git push origin main -f")

    if result == 0:
        print("✅ GitHub Updated Successfully with Force Push!")
    else:
        print("❌ Push failed. Check your GitHub Token or SSH Key.")


def main():
    """पूरा प्रोसेस शुरू करना"""
    header_str = fetch_from_api()

    if not header_str:
        print("Switching to backup...")
        header_str = fetch_from_backup()

    if not header_str:
        print("❌ No valid cookie found from any source")
        return

    update_all_links(header_str)
    git_push()

    print("\n✅ All done!")


if __name__ == "__main__":
    main()
