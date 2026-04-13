import requests
import re
import json

# Configuration
API_URL = "https://host.cloudplay.me/app/icc/hstr.php"
M3U_FILE_PATH = "Aki.m3u"  # Aapki repo me jo file hai uska naam

def fetch_api_data():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching API: {e}")
        return None

def update_m3u():
    api_data = fetch_api_data()
    if not api_data:
        return

    # API data ko channel name ke hisab se map kar lete hain fast lookup ke liye
    # Note: Kuch APIs list return karti hain, kuch object. 
    # Agar list hai to: {item['name']: item for item in api_data}
    channels_map = {}
    if isinstance(api_data, list):
        for item in api_data:
            channels_map[item['name'].lower()] = item
    elif isinstance(api_data, dict):
        # Agar API direct ek list nahi balki nested object hai
        data_list = api_data.get('data', []) # Adjust based on actual JSON structure
        for item in data_list:
            channels_map[item['name'].lower()] = item

    with open(M3U_FILE_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        # Check if line contains the specific domain
        if "jcevents.hotstar.com" in line:
            # Channel name extract karne ki koshish (tvg-name se)
            name_match = re.search(r'tvg-name="([^"]+)"', line)
            if not name_match:
                # Fallback: line ke end se name nikalna
                name_match = re.search(r',\s*(.*)$', line)
            
            if name_match:
                channel_name = name_match.group(1).lower().strip()
                
                if channel_name in channels_map:
                    target = channels_map[channel_name]
                    m3u8_url = target.get('m3u8_url')
                    cookie = target.get('headers', {}).get('Cookie', '')
                    ua = target.get('user_agent', '')
                    origin = target.get('headers', {}).get('Origin', 'https://www.hotstar.com')
                    referer = target.get('headers', {}).get('Referer', 'https://www.hotstar.com/')

                    # Naya format assembly
                    updated_url_line = f"{m3u8_url}|Cookie=\"{cookie}\"&User-Agent=\"{ua}\"&Origin=\"{origin}\"&Referer=\"{referer}\"\n"
                    new_lines.append(updated_url_line)
                    continue
        
        new_lines.append(line)

    with open(M3U_FILE_PATH, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("M3U file updated successfully!")

if __name__ == "__main__":
    update_m3u()
