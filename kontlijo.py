import requests
import time
from datetime import datetime
from colorama import init, Fore, Style
from itertools import cycle
from threading import Thread

init(autoreset=True)
BASE_URL = "https://api.dashboard.3dos.io"

def load_tokens():
    try:
        with open("token.txt", "r") as file:
            tokens = [line.strip() for line in file if line.strip()]
            if not tokens:
                raise ValueError("No tokens found in token.txt")
            return tokens
    except FileNotFoundError:
        print(Fore.RED + "[ERROR] File 'tokens.txt' not found. Please create a file named 'token.txt' and add your tokens.")
        exit(1)
    except Exception as e:
        print(Fore.RED + f"[ERROR] Failed to load tokens: {e}")
        exit(1)

def load_proxies():
    try:
        with open("proxy.txt", "r") as file:
            proxies = [line.strip() for line in file if line.strip()]
            return proxies
    except FileNotFoundError:
        print(Fore.YELLOW + "[WARNING] File 'proxy.txt' not found. Using direct connection without proxies.")
        return []
    except Exception as e:
        print(Fore.RED + f"[ERROR] Failed to load proxies: {e}")
        return []

def make_post_request(endpoint, headers, data=None, proxy=None):
    url = f"{BASE_URL}{endpoint}"
    try:
        proxies = {"http": proxy, "https": proxy} if proxy else None
        response = requests.post(url, headers=headers, json=data, proxies=proxies, timeout=10)
        return response
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}[{datetime.now()}] Request failed with proxy {proxy}: {e}")
        return None

def process_token(token, proxies):
    headers_general = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "authorization": f"Bearer {token}",
        "cache-control": "no-cache",
        "content-type": "application/json",
        "origin": "https://dashboard.3dos.io",
        "pragma": "no-cache",
        "referer": "https://dashboard.3dos.io/",
        "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    }

    proxy_cycle = cycle(proxies) if proxies else None

    while True:
        try:
            # Try all proxies in the list
            success = False
            for _ in range(len(proxies) if proxies else 1):
                proxy = next(proxy_cycle) if proxy_cycle else None
                print(f"{Fore.CYAN}[{datetime.now()}] Connecting with proxy: {proxy if proxy else 'Direct Connection'} for token {token[:10]}...")
                profile_response = make_post_request("/api/profile/me", headers_general, {}, proxy)
                if profile_response and profile_response.status_code == 200:
                    success = True
                    break

            # Fallback to direct connection if all proxies fail
            if not success and proxies:
                print(f"{Fore.YELLOW}[{datetime.now()}] Retrying with direct connection for token {token[:10]}...")
                profile_response = make_post_request("/api/profile/me", headers_general, {}, None)

            if not profile_response or profile_response.status_code != 200:
                print(f"{Fore.RED}[{datetime.now()}] Profile sync failed for token {token[:10]}...")
                time.sleep(10)
                continue

            profile_data = profile_response.json()
            status = profile_data.get("status")
            email = profile_data.get("data", {}).get("email")
            loyalty_points = profile_data.get("data", {}).get("loyalty_points")

            print(f"{Fore.GREEN}[PROFILE DATA for token {token[:10]}...]")
            print(f"{Fore.CYAN}Status: {status}")
            print(f"{Fore.CYAN}Email: {email}")
            print(f"{Fore.CYAN}Loyalty Points: {loyalty_points}")

            api_secret = profile_data.get("data", {}).get("api_secret")
            if api_secret:
                print(f"{Fore.GREEN}[{datetime.now()}] API Secret Found: {api_secret}")
                profile_api_endpoint = f"/api/profile/api/{api_secret}"
                profile_api_response = make_post_request(profile_api_endpoint, headers_general, {}, proxy)
                if profile_api_response and profile_api_response.status_code == 200:
                    profile_api_data = profile_api_response.json().get("data", {})
                    print(f"{Fore.GREEN}[PROFILE API DATA for token {token[:10]}...]")
                    print(f"{Fore.CYAN}Username: {profile_api_data.get('username')}")
                    print(f"{Fore.CYAN}Tier: {profile_api_data.get('tier', {}).get('tier_name')}")
                    print(f"{Fore.CYAN}Next Tier: {profile_api_data.get('next_tier', {}).get('tier_name')}")
                    print(f"{Fore.CYAN}Daily Reward Claim: {profile_api_data.get('daily_reward_claim')}")
                else:
                    print(f"{Fore.RED}[{datetime.now()}] Profile API request failed for token {token[:10]}...")
            else:
                print(f"{Fore.RED}[{datetime.now()}] API Secret not found for token {token[:10]}...")

            time.sleep(10)

        except Exception as e:
            print(f"{Fore.RED}[{datetime.now()}] An error occurred for token {token[:10]}...: {e}")
            time.sleep(10)

def main():
    tokens = load_tokens()
    proxies = load_proxies()
    threads = []

    for token in tokens:
        thread = Thread(target=process_token, args=(token, proxies))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
