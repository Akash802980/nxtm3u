import requests
import re
import json

API_URL = "https://host.cloudplay.me/app/icc/hstr.php"
M3U_FILE = "Aki.m3u" # Apni file ka naam check kar lena

def get_latest_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        r = requests.get(API_URL, headers=headers, timeout=15)
        
        # Check agar status code 200 hai
        if r.status_code != 200:
            print(f"Server returned error: {r.status_code}")
            return None
            
        # Debugging: Print first 100 chars of response if it fails
        try:
            return {item['m3u8_url']: item for item in r.json()}
        except json.JSONDecodeError:
            print("Response was not JSON. Raw response starts with:")
            print(r.text[:200])
            return None
            
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def patch_m3u():
    new_data_map = get_latest_data()
    if not new_data_map:
        print("API se data nahi mila. Exiting...")
        return

    try:
        with open(M3U_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: {M3U_FILE} nahi mili!")
        return

    updated_lines = []
    count = 0

    for line in lines:
        if "jcevents.hotstar.com" in line:
            # Extract URL (split by | if it exists)
            current_url = line.split('|')[0].strip()
            
            if current_url in new_data_map:
                info = new_data_map[current_url]
                cookie = info.get('headers', {}).get('Cookie', '')
                ua = info.get('user_agent', '')
                origin = info.get('headers', {}).get('Origin', 'https://www.hotstar.com')
                referer = info.get('headers', {}).get('Referer', 'https://www.hotstar.com/')
                
                new_line = f"{current_url}|Cookie=\"{cookie}\"&User-Agent=\"{ua}\"&Origin=\"{origin}\"&Referer=\"{referer}\"\n"
                updated_lines.append(new_line)
                count += 1
                continue
        
        updated_lines.append(line)

    with open(M3U_FILE, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)
    
    print(f"Successfully updated {count} channels.")

if __name__ == "__main__":
    patch_m3u()
