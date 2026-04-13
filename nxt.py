import requests
import re

# Settings
API_URL = "https://host.cloudplay.me/app/icc/hstr.php"
M3U_FILE = "playlist.m3u"  # Tumhari file ka naam

def get_latest_data():
    try:
        r = requests.get(API_URL, timeout=10)
        data = r.json()
        # Agar data list mein hai toh usko dict mein convert kar rahe hain for easy lookup
        # Hum 'm3u8_url' ko key bana rahe hain taaki exact link match ho sake
        return {item['m3u8_url']: item for item in data}
    except Exception as e:
        print(f"API Error: {e}")
        return None

def patch_m3u():
    new_data_map = get_latest_data()
    if not new_data_map:
        return

    updated_lines = []
    
    with open(M3U_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        # Check agar line mein hotstar ka domain hai
        if "jcevents.hotstar.com" in line:
            # Line se purana m3u8 link nikalte hain (pipe '|' se pehle wala part)
            current_url = line.split('|')[0].strip()
            
            # Agar ye URL hamare API data mein maujood hai
            if current_url in new_data_map:
                info = new_data_map[current_url]
                cookie = info['headers']['Cookie']
                ua = info['user_agent']
                origin = info['headers']['Origin']
                referer = info['headers']['Referer']
                
                # Nayi line generate karna formatted way mein
                new_line = f"{current_url}|Cookie=\"{cookie}\"&User-Agent=\"{ua}\"&Origin=\"{origin}\"&Referer=\"{referer}\"\n"
                updated_lines.append(new_line)
                continue
        
        # Agar domain match nahi hua ya API mein link nahi mila toh purani line rehne do
        updated_lines.append(line)

    with open(M3U_FILE, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)
    print("Done! Cookies update ho gayi hain.")

if __name__ == "__main__":
    patch_m3u()
