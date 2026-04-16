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

#  PRIMARY SOURCE (API)
def fetch_from_api():
    print("Trying API...")
    try:
        res = requests.get(API_URL, timeout=10)
        data = res.json()
        for ch in data:
            url = ch.get("m3u8_url", "")
            if any(d in url for d in HOTSTAR_DOMAINS):
                print("API cookie found ")
                return build_header(ch.get("headers", {}), ch.get("user_agent", ""))
    except Exception as e:
        print("API Failed ", e)
    return None

#  BACKUP SOURCE
def fetch_from_backup():
    print("Trying Backup M3U...")
    headers = {
        "User-Agent": "TiviMate/5.1.0 (Android 13)",
        "Accept-Encoding": "gzip"
    }
    try:
        res = requests.get(BACKUP_M3U, headers=headers, timeout=15)
        text = res.text
        lines = text.splitlines()
        for line in lines:
            if any(d in line for d in HOTSTAR_DOMAINS) and "|" in line:
                header_part = line.split("|", 1)[1].strip()
                print("Backup cookie found ")
                return header_part
    except Exception as e:
        print("Backup Failed ", e)
    return None

#  UPDATE M3U FILE
def update_all_links(header_str):
    print(f"Updating {M3U_FILE}...")
    if not os.path.exists(M3U_FILE):
        #            
        open(M3U_FILE, "w").close()

    with open(M3U_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    domain_count = {d: 0 for d in HOTSTAR_DOMAINS}

    for line in lines:
        if any(d in line for d in HOTSTAR_DOMAINS):
            base_url = line.split("|")[0].strip()
            new_line = f"{base_url}|{header_str}\n"
            for d in HOTSTAR_DOMAINS:
                if d in line: domain_count[d] += 1
            new_lines.append(new_line)
        else:
            new_lines.append(line)

    #  FORCE TIMESTAMP ( Git    )
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not any("#EXTM3U" in l for l in new_lines):
        new_lines.insert(0, "#EXTM3U\n")
    
    new_lines.insert(1, f"# Last Updated: {timestamp}\n")

    with open(M3U_FILE, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print(" Update Summary:")
    for d, count in domain_count.items():
        print(f"{d}  {count} links updated")

#  GIT FORCE PUSH (    )
def git_push():
    print("\n Syncing with GitHub (Force Mode)...")
    
    # Git identity   ( )
    os.system('git config user.name "Github Bot"')
    os.system('git config user.email "bot@github.com"')

    # 
    os.system("git add .")

    #      
    status = os.popen("git status --porcelain").read().strip()
    if not status:
        print(" No changes to commit.")
        return

    # 
    msg = f"Auto update {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    os.system(f'git commit -m "{msg}"')

    #  FORCE PUSH:        
    print(" Pushing to origin main...")
    result = os.system("git push origin main --force")

    if result == 0:
        print(" GitHub Updated Successfully!")
    else:
        print(" Push failed! Check if your Token/SSH has Write access.")

#  MAIN
def main():
    #       (   )
    os.system("git pull origin main")

    header_str = fetch_from_api()
    if not header_str:
        print("Switching to backup...")
        header_str = fetch_from_backup()

    if not header_str:
        print("No valid cookie found ")
        return

    update_all_links(header_str)
    git_push()
    print("\n All tasks completed!")

if __name__ == "__main__":
    main()
