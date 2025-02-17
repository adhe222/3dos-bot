import requests
import time
from colorama import init, Fore, Style

init(autoreset=True)

base_url = "https://api.dashboard.3dos.io"

def load_proxies(file_path):
    try:
        with open(file_path, 'r') as file:
            proxies = [line.strip() for line in file if line.strip()]
        return proxies
    except FileNotFoundError:
        print(Fore.RED + Style.BRIGHT + f"File {file_path} not found.")
        return []

def load_keys(file_path):
    try:
        with open(file_path, 'r') as file:
            keys = [line.strip() for line in file if line.strip()]
        return keys
    except FileNotFoundError:
        print(Fore.RED + Style.BRIGHT + f"File {file_path} not found.")
        return []

accounts = [
    {"username": "Account1", "auth_key": "initial_auth_key_1"},
    {"username": "Account2", "auth_key": "initial_auth_key_2"},
]

proxies = load_proxies("proxy.txt")
keys = load_keys("keygen.txt")

while True:
    for account in accounts:
        username = account["username"]
        auth_key = account["auth_key"]

        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Authorization": f"Bearer {auth_key}",
            "Host": "api.dashboard.3dos.io",
            "Origin": "chrome-extension://lpindahibbkakkdjifonckbhopdoaooe",
            "refferer": "https://dashboard.3dos.io/register?ref_code=1c744d",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "none",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
        }

        proxy_list = proxies if proxies else [None]

        for proxy in proxy_list:
            proxy_dict = {"http": proxy, "https": proxy} if proxy else None

            for key in keys:
                try:
                    post_endpoint = f"/api/profile/api/{key}"
                    post_url = base_url + post_endpoint
                    post_response = requests.post(post_url, headers=headers, proxies=proxy_dict, timeout=10)

                    if post_response.status_code == 200:
                        post_data = post_response.json()
                        email = post_data.get("data", {}).get("email", "N/A")
                        cookie = post_response.headers.get("Set-Cookie", "N/A")

                        print(Fore.CYAN + Style.BRIGHT + f"=== Koneksi Berhasil [{username}] ===")
                        print(Fore.GREEN + Style.BRIGHT + f"Username: {username}")
                        print(Fore.GREEN + Style.BRIGHT + f"Email: {email}")
                        print(Fore.GREEN + Style.BRIGHT + f"Cookie: {cookie}")
                        print(Fore.YELLOW + Style.BRIGHT + (f"Proxy: {proxy}" if proxy else "No Proxy Used"))
                        headers["Cookie"] = cookie

                    else:
                        print(Fore.RED + Style.BRIGHT + f"POST Request Failed [{username}] with Status Code: {post_response.status_code}")
                        print(Fore.YELLOW + Style.BRIGHT + (f"Proxy: {proxy}" if proxy else "No Proxy Used"))

                    get_endpoint = f"/api/refresh-points/{key}"
                    get_url = base_url + get_endpoint
                    get_response = requests.get(get_url, headers=headers, proxies=proxy_dict, timeout=10)

                    if get_response.status_code == 200:
                        get_data = get_response.json()
                        total_points = get_data.get("data", {}).get("total_points", "N/A")

                        print(Fore.GREEN + Style.BRIGHT + f"Total Points: {total_points}")
                        print(Fore.YELLOW + Style.BRIGHT + (f"Proxy: {proxy}" if proxy else "No Proxy Used"))
                        print(Fore.CYAN + "=" * 50)

                    else:
                        print(Fore.RED + Style.BRIGHT + f"GET Request Failed [{username}] with Status Code: {get_response.status_code}")
                        print(Fore.YELLOW + Style.BRIGHT + (f"Proxy: {proxy}" if proxy else "No Proxy Used"))

                except requests.exceptions.RequestException as e:
                    print(Fore.RED + Style.BRIGHT + f"An error occurred for [{username}] using proxy {proxy} and key {key}:")
                    print(Fore.RED + str(e))

    time.sleep(4)
