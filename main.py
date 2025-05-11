# https://colab.research.google.com/ 
# ^^ that website allows for testing on google's servers.
# again this thing sucks, go use Sherlock.

import requests
import time
import random
from collections import defaultdict

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.86 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.57 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.86 Safari/537.36 Edg/123.0.2420.53",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13.3; rv:124.0) Gecko/20100101 Firefox/124.0"
]

platforms = {
    "Twitter": "https://twitter.com/{}",
    "TikTok": "https://www.tiktok.com/@{}",
    "GitHub": "https://github.com/{}",
    "Reddit": "https://www.reddit.com/user/{}",
    "YouTube": "https://www.youtube.com/@{}",
    "Twitch": "https://www.twitch.tv/{}",
    "SoundCloud": "https://soundcloud.com/{}",
    "Roblox": "https://www.roblox.com/users/profile?username={}"
}

def check_username(username):
    found = []
    errors = []

    for platform, url_template in platforms.items():
        url = url_template.format(username)
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
        }

        try:
            res = requests.get(url, headers=headers, timeout=3, allow_redirects=True)

            if res.status_code == 200 or res.status_code in [301, 302]:
                found.append((platform, res.url))
            elif res.status_code in [403, 429]:
                desc = {
                    403: "Forbidden (maybe blocked by bot protection)",
                    429: "Too Many Requests (rate-limited)"
                }.get(res.status_code, f"Error {res.status_code}")
                errors.append((platform, desc))

        except Exception as e:
            errors.append((platform, f"Error {str(e)}"))

    return found, errors

if __name__ == "__main__":
    while True:
        try:
            user_input = input("[ - ] Enter usernames for lookup: ").strip()
            usernames = [u.strip() for u in user_input.split(",") if u.strip()]

            found_by_platform = defaultdict(list)
            errors_by_platform = defaultdict(list)

            for username in usernames:
                found, errors = check_username(username)
                for platform, url in found:
                    found_by_platform[platform].append(f"{url}")
                for platform, err in errors:
                    errors_by_platform[platform].append(f"{username}: {err}")

            for platform, urls in found_by_platform.items():
                print(f"[+] {platform}:")
                for url in urls:
                    print(f"    {url}")

            print("\n=== Errors ===")
            for platform, errlist in errors_by_platform.items():
                print(f"[+] {platform}:")
                for err in errlist:
                    print(f"    {err}")

            print("\n---\n")
            time.sleep(10)

        except KeyboardInterrupt:
            print("\nExiting.")
            break
