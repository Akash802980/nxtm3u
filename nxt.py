import cloudscraper
import re

json_url = "https://allinonereborn.fun/jstrweb2/index.php"
m3u_file = "Aki.m3u"

# cloudscraper client banate hai
scraper = cloudscraper.create_scraper(browser={"browser":"chrome","platform":"android","mobile":True})
resp = scraper.get(json_url)

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
