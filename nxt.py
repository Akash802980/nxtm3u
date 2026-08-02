import requests

# ==========================
# Configuration
# ==========================

WORKER_URL = "https://sonyliv.joker-verse.workers.dev/master.m3u8?id=1000009248&uid=1045595420&pass=169ae613"

M3U_FILE = "Aki.m3u"

headers = {
    "Origin": "https://www.sonyliv.com",
    "Referer": "https://www.sonyliv.com/",
    "User-Agent": "TiviMate/5.1.0"
}

# ==========================
# Get latest token
# ==========================

print("Getting latest token...")

response = requests.get(
    WORKER_URL,
    headers=headers,
    allow_redirects=False,
    timeout=15
)

if response.status_code not in (301, 302):
    print("Worker did not return redirect!")
    print(response.status_code)
    exit()

redirect_url = response.headers.get("Location")

if not redirect_url:
    print("Redirect URL not found!")
    exit()

print("Redirect URL:")
print(redirect_url)

# Extract latest token
token = redirect_url.split("?", 1)[1]

print("\nLatest Token:")
print(token)

# ==========================
# Read playlist
# ==========================

with open(M3U_FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

updated = []
count = 0

for line in lines:
    if line.startswith("https://dishmt.slivcdn.com"):
        base = line.strip().split("?", 1)[0]
        updated.append(base + "?" + token + "\n")
        count += 1
    else:
        updated.append(line)

# ==========================
# Overwrite same file
# ==========================

with open(M3U_FILE, "w", encoding="utf-8") as f:
    f.writelines(updated)

print(f"\nDone! {count} links updated in {M3U_FILE}")
