from optparse import Option
import requests, threading, os, time, subprocess
from colorama import Fore, init
import json
import fade
import ctypes
import sys
import pkg_resources

# Initialization
init(autoreset=True)
os.system('cls' if os.name == 'nt' else 'clear')
ctypes.windll.kernel32.SetConsoleTitleW("Ironluca's Boost Tool")

# Automatically install required packages
required_packages = {
    'requests': 'requests',
    'colorama': 'colorama',
    'fade': 'fade',
    'capmonster-python': 'capmonster-python'
}

def install_packages():
    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing_packages = [pkg for pkg in required_packages.values() if pkg not in installed]
    
    if missing_packages:
        print(f"{Fore.YELLOW}[INFO] Installing missing packages: {', '.join(missing_packages)}")
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"{Fore.GREEN}[SUCCESS] Installed {package}")
            except subprocess.CalledProcessError as e:
                print(f"{Fore.RED}[ERROR] Failed to install {package}: {e}")
                sys.exit(1)
    else:
        print(f"{Fore.GREEN}[INFO] All required packages are already installed.")

# Run setup
install_packages()
os.system('cls' if os.name == 'nt' else 'clear')  # Clear terminal after installation

# Debug: Print current working directory and script path
print(f"{Fore.YELLOW}[DEBUG] Current working directory: {os.getcwd()}")
print(f"{Fore.YELLOW}[DEBUG] Script directory: {os.path.dirname(os.path.abspath(__file__))}")

# Load configuration
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, 'settings.json')
print(f"{Fore.YELLOW}[DEBUG] Looking for settings.json at: {config_path}")
try:
    with open(config_path) as config_file:
        config = json.load(config_file)
        CAPMONSTER_KEY = config['apikey']
except FileNotFoundError:
    print(f"{Fore.RED}[ERROR] 'settings.json' not found at: {config_path}")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"{Fore.RED}[ERROR] 'settings.json' contains invalid JSON")
    sys.exit(1)
except KeyError:
    print(f"{Fore.RED}[ERROR] 'settings.json' is missing 'apikey' field")
    sys.exit(1)
except Exception as e:
    print(f"{Fore.RED}[ERROR] Failed to load 'settings.json': {e}")
    sys.exit(1)

# Global variables
done = 0
retries = 0
bypass = 0

# Adjust console size (Windows)
if os.name == 'nt':
    os.system('mode 60,30')

def print_banner(boosts_amount: int):
    banner = fade.fire(f"""
{Fore.CYAN}════════════════════════════════════════════════════
{Fore.YELLOW}         IRONLUCA Discord Boost Tool
{Fore.CYAN}════════════════════════════════════════════════════
{Fore.WHITE}            Created by: @Ironlucaaa
{Fore.WHITE}            Boosts Available: {Fore.GREEN}{boosts_amount}{Fore.WHITE}
{Fore.CYAN}════════════════════════════════════════════════════
{Fore.YELLOW}[1] Boost Server
{Fore.YELLOW}[2] Edit Token Stock
{Fore.YELLOW}[3] Exit
{Fore.CYAN}════════════════════════════════════════════════════
    """)
    print(banner)

def get_fingerprint():
    try:
        r = requests.get('https://discord.com/api/v9/experiments')
        if r.status_code == 200:
            return r.json()['fingerprint']
        else:
            print(f"{Fore.RED}[ERROR] Could not retrieve fingerprint: {r.status_code}")
            return None
    except Exception as e:
        print(f"{Fore.RED}[ERROR] Error retrieving fingerprint: {e}")
        return None

def get_cookies():
    try:
        r = requests.get('https://discord.com')
        if r.status_code == 200:
            cookies = r.cookies.get_dict()
            return f"__dcfduid={cookies['__dcfduid']}; __sdcfduid={cookies['__sdcfduid']}; locale=en-US"
        else:
            print(f"{Fore.RED}[ERROR] Could not retrieve cookies: {r.status_code}")
            return None
    except Exception as e:
        print(f"{Fore.RED}[ERROR] Error retrieving cookies: {e}")
        return None

def load_tokens():
    try:
        token_path = os.path.join(script_dir, 'tokens.txt')
        print(f"{Fore.YELLOW}[DEBUG] Looking for tokens.txt at: {token_path}")
        with open(token_path, "r", encoding='utf-8') as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        print(f"{Fore.RED}[ERROR] tokens.txt not found at: {token_path}")
        return []
    except Exception as e:
        print(f"{Fore.RED}[ERROR] Error loading tokens: {e}")
        return []

def save_tokens(tokens):
    try:
        token_path = os.path.join(script_dir, 'tokens.txt')
        with open(token_path, "w", encoding='utf-8') as f:
            f.write("\n".join(tokens))
    except Exception as e:
        print(f"{Fore.RED}[ERROR] Error saving tokens: {e}")

def remove_duplicates(file):
    try:
        tokens = load_tokens()
        unique_tokens = list(dict.fromkeys(tokens))  
        save_tokens(unique_tokens)
        return len(unique_tokens)
    except Exception as e:
        print(f"{Fore.RED}[ERROR] Error removing duplicates: {e}")
        return 0

def boost(token, invite):
    global done  
    global retries, bypass
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'en-US',
        'authorization': token,
        'content-type': 'application/json',
        'origin': 'https://discord.com',
        'referer': 'https://discord.com/channels/@me',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'x-debug-options': 'bugReporterEnabled',
        'x-context-properties': 'eyJsb2NhdGlvbiI6IlVzZXIgUHJvZmlsZSJ9',
        'x-super-properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiY2xpZW50X2J1aWxkX251bWJlciI6MTAwMDAwfQ==',
        'cookie': get_cookies() or '',
    }

    try:
        r = requests.get("https://discord.com/api/v9/users/@me/guilds/premium/subscription-slots", headers=headers)
        if r.status_code == 200:
            slots = r.json()
            if not slots:
                print(f"{Fore.YELLOW}[INFO] No boost slots for token: {token[:10]}...")
                return False

            guid = None
            for attempt in range(3):  
                try:
                    join_server = requests.post(f"https://discord.com/api/v9/invites/{invite}", headers=headers, json={})
                    if "captcha_sitekey" in join_server.text:
                        print(f"{Fore.YELLOW}[INFO] Captcha detected, solving with Capmonster...")
                        capmonster = RecaptchaV2Task(CAPMONSTER_KEY)
                        task_id = capmonster.create_task("https://discord.com/channels/@me", join_server.json()['captcha_sitekey'])
                        solution = capmonster.join_task_result(task_id)
                        captcha_key = solution.get("gRecaptchaResponse")

                        print(f"{Fore.GREEN}[SUCCESS] Captcha solved!")
                        join_server = requests.post(f"https://discord.com/api/v9/invites/{invite}", headers=headers, json={"captcha_key": captcha_key})

                    if join_server.status_code == 200:
                        guid = join_server.json()["guild"]["id"]
                        print(f"{Fore.GREEN}[SUCCESS] Joined server with token: {token[:10]}...")
                        break
                    else:
                        print(f"{Fore.RED}[ERROR] Error joining server: {join_server.status_code} - {join_server.text}")
                        retries += 1
                        return False
                except Exception as e:
                    print(f"{Fore.RED}[ERROR] Error joining server: {e}")
                    retries += 1
                    time.sleep(1)

            if not guid:
                return False

            # Perform boost
            for slot in slots:
                slot_id = slot['id']
                payload = {"user_premium_guild_subscription_slot_ids": [slot_id]}
                r2 = requests.put(f'https://discord.com/api/v9/guilds/{guid}/premium/subscriptions', headers=headers, json=payload)
                if r2.status_code == 201:
                    done += 1
                    print(f"{Fore.GREEN}[SUCCESS] Boost successful: {token[:10]}... (Slot ID: {slot_id})")
                else:
                    print(f"{Fore.RED}[ERROR] Boost failed: {r2.status_code} - {r2.text}")
                    retries += 1
            return True
        else:
            print(f"{Fore.RED}[ERROR] Token invalid or banned: {token[:10]}... ({r.status_code})")
            retries += 1
            return False
    except Exception as e:
        print(f"{Fore.RED}[ERROR] General error with token: {token[:10]}... ({e})")
        retries += 1
        return False

def main():
    global done  
    tokens = load_tokens()
    boosts_amount = len(tokens) * 2 
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print_banner(boosts_amount)
        choice = input(f"{Fore.CYAN}>> Choose an option: {Fore.WHITE}")

        if choice == "1":
            invite = input(f"{Fore.CYAN}>> Discord Invite Code (e.g., 'xyz123'): {Fore.WHITE}")
            try:
                boost_amount = int(input(f"{Fore.CYAN}>> Number of Boosts: {Fore.WHITE}"))
            except ValueError:
                print(f"{Fore.RED}[ERROR] Invalid input! Please enter a number.")
                time.sleep(2)
                continue

            valid_tokens = tokens[:]
            for token in tokens:
                if done >= boost_amount:
                    break
                if boost(token, invite):
                    valid_tokens.remove(token)
            save_tokens(valid_tokens)
            print(f"{Fore.GREEN}[SUCCESS] Boosting completed! {done} boosts performed.")
            boosts_amount = len(valid_tokens) * 2
            done = 0  
            time.sleep(3)

        elif choice == "2":
            token_path = os.path.join(script_dir, 'tokens.txt')
            print(f"{Fore.YELLOW}[DEBUG] Opening tokens.txt at: {token_path}")
            if os.name == 'nt':
                os.system(f"notepad \"{token_path}\"")  
            else:
                os.system(f"nano \"{token_path}\"")  
            tokens = load_tokens()
            boosts_amount = len(tokens) * 2
            print(f"{Fore.GREEN}[INFO] Token stock updated. New boosts available: {boosts_amount}")
            time.sleep(2)

        elif choice == "3":
            print(f"{Fore.YELLOW}[INFO] Exiting IRONLUCA Boost Tool...")
            sys.exit(0)
        else:
            print(f"{Fore.RED}[ERROR] Invalid option! Choose 1, 2, or 3.")
            time.sleep(2)

if __name__ == "__main__":
    remove_duplicates("tokens.txt")
    main()