import requests
import re

json_url = "https://allinonereborn.fun/jst"
m3u_file = "playlist.m3u"

resp = requests.get(json_url, headers={"User-Agent": "Mozilla/5.0"})
data = resp.json()
new_token = data[0]["token"]

with open(m3u_file, "r", encoding="utf-8") as f:
    content = f.read()

# remove old token from mpd URLs
content = re.sub(r"\?__hdnea__=.*", "", content)

# add new token to mpd URLs
content = re.sub(
    r"(https://jiotvmblive\.cdn\.jio\.com[^\s]+?\.mpd)",
    rf"\1?{new_token}",
    content
)

# update token in #EXTHTTP cookie line
content = re.sub(
    r'(#EXTHTTP:{"cookie":")__hdnea__=.*?"}',
    rf'\1{new_token}"',
    content
)

with open(m3u_file, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Playlist updated with token:", new_token)
