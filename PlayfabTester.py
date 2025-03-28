import requests
import colorama
from colorama import Fore, Style
import uuid
import time
import os
import math
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

def countdown():
    for i in range(3, 0, -1):
        print(f"{Fore.MAGENTA}Restarting in {i}...{Style.RESET_ALL}")
        time.sleep(1)
    clear_screen()

def load_proxies():
    try:
        with open('proxies.txt', 'r') as f:
            proxies = [line.strip() for line in f if line.strip()]
        return proxies
    except FileNotFoundError:
        print(f"{Fore.RED}Proxies file not found.{Style.RESET_ALL}")
        return []

def send_request(title_id, proxy=None):
    custom_id = str(uuid.uuid4())
    url = f"https://{title_id}.playfabapi.com/Client/LoginWithCustomID"
    
    headers = {
        "Content-Type": "application/json",
    }
    
    data = {
        "TitleId": title_id,
        "CustomId": custom_id,
        "CreateAccount": True
    }
    
    proxies = {
        "http": f"http://{proxy}",
        "https": f"http://{proxy}"
    } if proxy else None
    
    try:
        response = requests.post(
            url,
            json=data,
            headers=headers,
            proxies=proxies,
            timeout=10
        )
        return response.status_code
    except Exception as e:
        return str(e)

def send_webhook(webhook_url, progress):
    try:
        requests.post(webhook_url, json={
            "embeds": [{
                "title": "PlayFab Tester Progress",
                "description": f"Progress: {progress:.2f}%",
                "color": 0x800080
            }]
        })
    except:
        pass

def main():
    clear_screen()
    print(BANNER)
    
    webhook_url = input(f"{Fore.MAGENTA}Enter Discord webhook URL (press Enter to skip): {Style.RESET_ALL}").strip()
    title_id = input(f"{Fore.MAGENTA}Enter PlayFab Title ID: {Style.RESET_ALL}").strip()
    request_count = int(input(f"{Fore.MAGENTA}Enter number of requests to send: {Style.RESET_ALL}"))
    
    proxies = load_proxies()
    proxy_cycle = iter(proxies) if proxies else None
    
    successful = 0
    failed = 0
    
    for i in range(1, request_count + 1):
        proxy = next(proxy_cycle) if proxy_cycle else None
        status = send_request(title_id, proxy)
        
        if isinstance(status, int) and status == 200:
            successful += 1
            print(f"{Fore.GREEN}Request {i}/{request_count} successful{Style.RESET_ALL}")
        else:
            failed += 1
            print(f"{Fore.RED}Request {i}/{request_count} failed: {status}{Style.RESET_ALL}")
        
        # Progress reporting (every 4%)
        if request_count >= 25 and i % (request_count // 25) == 0:
            progress = (i / request_count) * 100
            print(f"{Fore.MAGENTA}Progress: {progress:.2f}%{Style.RESET_ALL}")
            
            if webhook_url:
                send_webhook(webhook_url, progress)
    
    print(f"\n{Fore.MAGENTA}Summary:{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Successful: {successful}{Style.RESET_ALL}")
    print(f"{Fore.RED}Failed: {failed}{Style.RESET_ALL}")
    
    countdown()
    main()

if __name__ == "__main__":
    main()
