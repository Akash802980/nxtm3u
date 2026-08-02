import requests

url = "https://sonyliv.joker-verse.workers.dev/master.m3u8?id=1000009248&uid=1045595420&pass=169ae613"

headers = {
    "Origin": "https://www.sonyliv.com",
    "Referer": "https://www.sonyliv.com/",
    "User-Agent": "TiviMate/5.1.0"
}

try:
    # Don't follow redirect
    response = requests.get(
        url,
        headers=headers,
        allow_redirects=False,
        timeout=10
    )

    print("Status Code:", response.status_code)

    if response.status_code in (301, 302, 303, 307, 308):
        print("\nRedirect URL:")
        print(response.headers.get("Location"))
    else:
        print(response.text)

except Exception as e:
    print("Error:", e)
