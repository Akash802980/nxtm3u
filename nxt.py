import requests
import re

API_URL = "https://host.cloudplay.me/app/icc/hstr.php"
M3U_FILE = "Aki.m3u"


def fetch_data():
    print("Fetching API...")

    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://host.cloudplay.me",
        "Referer": "https://host.cloudplay.me/",
        "Connection": "keep-alive"
    }

    try:
        res = session.get(API_URL, headers=headers, timeout=15)

        print("Status:", res.status_code)
        print("Preview:", res.text[:150])

        # JSON try
        data = res.json()
        return data

    except Exception as e:
        print("FAILED:", e)
        return None


if __name__ == "__main__":
    fetch_data()
