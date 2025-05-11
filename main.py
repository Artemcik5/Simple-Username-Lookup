# https://colab.research.google.com/
# ^^ Use that website for the tool.

import requests
import random
import time
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
    "Reddit": "https://www.reddit.com/user/{}/",
    "YouTube": "https://www.youtube.com/@{}",
    "Twitch": "https://www.twitch.tv/{}",
    "SoundCloud": "https://soundcloud.com/{}",
    "Roblox": "https://www.roblox.com/users/profile?username={}",
    "Facebook": "https://www.facebook.com/{}/"
}

def check_username(username):
    found = []
    errors = []
    for platform, url_t in platforms.items():
        url = url_t.format(username)
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
        }
        try:
            r = requests.get(url, headers=headers, timeout=5, allow_redirects=True)
            text = r.text.lower()

            # Twitter: Check for specific error message in the response text
            if platform == "Twitter" and "sorry, that page doesn’t exist" in text:
                errors.append((platform, f"{username} does not exist (HTML check)"))
                continue

            # TikTok: Check for specific error message in the response text
            if platform == "TikTok" and "page not found" in text:
                errors.append((platform, f"{username} does not exist (HTML check)"))
                continue

            # Twitch: Check for specific error message in the response text
            if platform == "Twitch" and "data-a-target=\"core-error-message\"" in text:
                errors.append((platform, f"{username} does not exist (HTML check)"))
                continue

            # Facebook: Check for 400 status code and check if page exists
            if platform == "Facebook":
                if r.status_code == 400 and "this page isn’t available" in text:
                    errors.append((platform, f"{username} does not exist (HTML check)"))
                    continue
                elif r.status_code == 200:
                    found.append((platform, r.url))
                    continue
                else:
                    errors.append((platform, f"{username}: Unexpected status {r.status_code}"))
                    continue

            # General: Check for 404 status code
            if r.status_code == 404:
                errors.append((platform, f"{username} does not exist (404)"))
                continue

            # General: Check for 200 status code
            if r.status_code == 200:
                found.append((platform, r.url))
                continue

            # Handling Reddit-specific issues
            if platform == "Reddit":
                # Check for "user not found" or "page not found" text
                if "user not found" in text or "page not found" in text:
                    errors.append((platform, f"{username} does not exist (HTML check)"))
                # Check for CAPTCHA or robot verification challenge
                elif "captcha" in text or "verify you're not a robot" in text:
                    errors.append((platform, f"{username}: CAPTCHA challenge detected"))
                # Check for "403 Forbidden" or blocked access
                elif "access denied" in text or "403 forbidden" in text:
                    errors.append((platform, f"{username}: Blocked by Reddit (403 Forbidden)"))
                else:
                    found.append((platform, r.url))
                continue

            # General: Handle other status codes
            errors.append((platform, f"{username}: Unexpected status {r.status_code}"))

        except requests.exceptions.RequestException as e:
            errors.append((platform, f"{username}: Error {e}"))

    return found, errors

def wait_between_requests():
    # Random delay between 22 and 27 seconds
    time.sleep(random.randint(22, 27))

if __name__ == "__main__":
    while True:
        try:
            inp = input("[ - ] Enter usernames for lookup: ").strip()
            print("[!] This may take a while due to anti-bot and rate limiting..")
            print("[!] Platforms such as: Twitch, X (formerly Twitter), and Reddit are experimental and can have false positives/negatives.")
            users = [u.strip() for u in inp.split(",") if u.strip()]

            found_by_pl = defaultdict(list)
            errs_by_pl = defaultdict(list)

            for idx, u in enumerate(users):
                fnd, err = check_username(u)
                for p, link in fnd:
                    found_by_pl[p].append(link)
                for p, msg in err:
                    errs_by_pl[p].append(f"{u}: {msg}")

                # Wait between requests if there's more than one username to check
                if idx < len(users) - 1:
                    wait_between_requests()

            print("\n[✓] Found accounts:")
            for p, links in found_by_pl.items():
                print(f"  [{p}]")
                for l in links:
                    print(f"    → {l}")

            print("\n[✗] Errors / Not Found:")
            for p, msgs in errs_by_pl.items():
                print(f"  [{p}]")
                for m in msgs:
                    print(f"    → {m}")

            print("\n---\n")

        except KeyboardInterrupt:
            print("\nExiting.")
            break
