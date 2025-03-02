import requests
import time
from colorama import init, Fore, Style
import threading
import logging
import os

# Initialize colorama
init(autoreset=True)

# Configure logging with colorama for colored output
class ColoredFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Style.BRIGHT + Fore.RED,
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelno, '')
        message = super().format(record)
        return f"{log_color}{message}"

# Set up logging with colored formatter
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
formatter = ColoredFormatter()
handler = logging.getLogger().handlers[0]
handler.setFormatter(formatter)

base_url = "https://api.dashboard.3dos.io"
MAX_RETRIES = 5
BACKOFF_FACTOR = 2

def load_proxies(file_path):
    try:
        with open(file_path, 'r') as file:
            proxies = [line.strip() for line in file if line.strip()]
        return proxies
    except FileNotFoundError:
        logging.error(Fore.RED + Style.BRIGHT + f"File {file_path} not found.")
        return []

def load_keys(file_path):
    try:
        with open(file_path, 'r') as file:
            keys = [line.strip() for line in file if line.strip()]
        return keys
    except FileNotFoundError:
        logging.error(Fore.RED + Style.BRIGHT + f"File {file_path} not found.")
        return []

def exponential_backoff(retries):
    return BACKOFF_FACTOR ** retries * 0.1

def process_account(account, proxies, keys):
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
        "Referer": "https://dashboard.3dos.io/register?ref_code=1c744d",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "none",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }

    for proxy in proxies:
        proxy_dict = {"http": proxy, "https": proxy} if proxy else None

        for key in keys:
            retries = 0
            while retries < MAX_RETRIES:
                try:
                    post_endpoint = f"/api/profile/api/{key}"
                    post_url = base_url + post_endpoint
                    post_response = requests.post(post_url, headers=headers, proxies=proxy_dict, timeout=10)

                    if post_response.status_code == 200:
                        post_data = post_response.json()
                        email = post_data.get("data", {}).get("email", "N/A")
                        cookie = post_response.headers.get("Set-Cookie", "N/A")

                        logging.info(Fore.CYAN + Style.BRIGHT + f"=== Connection Successful [{username}] ===")
                        logging.info(Fore.GREEN + Style.BRIGHT + f"Username: {username}")
                        logging.info(Fore.GREEN + Style.BRIGHT + f"Email: {email}")
                        logging.info(Fore.GREEN + Style.BRIGHT + f"Cookie: {cookie}")
                        logging.info(Fore.YELLOW + Style.BRIGHT + (f"Proxy: {proxy}" if proxy else "No Proxy Used"))
                        headers["Cookie"] = cookie

                        break  # Exit the retry loop on success

                    else:
                        logging.error(Fore.RED + Style.BRIGHT + f"POST Request Failed [{username}] with Status Code: {post_response.status_code}")
                        logging.info(Fore.YELLOW + Style.BRIGHT + (f"Proxy: {proxy}" if proxy else "No Proxy Used"))

                    get_endpoint = f"/api/refresh-points/{key}"
                    get_url = base_url + get_endpoint
                    get_response = requests.get(get_url, headers=headers, proxies=proxy_dict, timeout=10)

                    if get_response.status_code == 200:
                        get_data = get_response.json()
                        total_points = get_data.get("data", {}).get("total_points", "N/A")

                        logging.info(Fore.GREEN + Style.BRIGHT + f"Total Points: {total_points}")
                        logging.info(Fore.YELLOW + Style.BRIGHT + (f"Proxy: {proxy}" if proxy else "No Proxy Used"))
                        logging.info(Fore.CYAN + Style.BRIGHT + "=" * 50)

                        break  # Exit the retry loop on success

                    else:
                        logging.error(Fore.RED + Style.BRIGHT + f"GET Request Failed [{username}] with Status Code: {get_response.status_code}")
                        logging.info(Fore.YELLOW + Style.BRIGHT + (f"Proxy: {proxy}" if proxy else "No Proxy Used"))

                    break  # Exit the retry loop on success

                except requests.exceptions.HTTPError as http_err:
                    if post_response.status_code == 429:
                        logging.warning(Fore.YELLOW + Style.BRIGHT + f"Rate limit exceeded for [{username}], retrying in {exponential_backoff(retries)} seconds...")
                        time.sleep(exponential_backoff(retries))
                        retries += 1
                        continue  # Continue to next retry iteration
                    else:
                        logging.error(Fore.RED + Style.BRIGHT + f"HTTP error occurred for [{username}]: {http_err}")
                        break  # Exit the retry loop on other HTTP errors

                except requests.exceptions.RequestException as e:
                    logging.error(Fore.RED + Style.BRIGHT + f"An error occurred for [{username}] using proxy {proxy} and key {key}:")
                    logging.error(Fore.RED + Style.BRIGHT + str(e))
                    break  # Exit the retry loop on other request exceptions

            if retries >= MAX_RETRIES:
                logging.error(Fore.RED + Style.BRIGHT + f"Max retries reached for [{username}] with proxy {proxy} and key {key}. Giving up.")

def main():
    accounts = [
        {"username": "Account1", "auth_key": "initial_auth_key_1"},
        {"username": "Account2", "auth_key": "initial_auth_key_2"},
    ]

    proxies = load_proxies(os.getenv("PROXY_FILE", "proxy.txt"))
    keys = load_keys(os.getenv("KEYGEN_FILE", "keygen.txt"))

    threads = []
    for account in accounts:
        thread = threading.Thread(target=process_account, args=(account, proxies, keys))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
