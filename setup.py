import json
import os
import subprocess
import sys

packages_installation_done = False
while not packages_installation_done:
    install_packages = input("Voulez-vous installer les paquets requis ? (O/n) : ")
    print(install_packages)
    if install_packages.lower() in ["o", "y", "oui", "yes", ""]:
        print("Installation des paquets")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        packages_installation_done = True
    elif install_packages.lower() in ["n", "non", "no"]:
        packages_installation_done = True


if not os.path.exists("datas"):
    os.mkdir("datas")

write_bot_file = True
if os.path.exists("datas/bot.json"):
    write_bot_file = False
    overwrite = input("Le fichier bot.json existe déjà, voulez-vous quand-même continuer ? (o/N)")
    
    if overwrite.lower() in ["o", "y", "oui", "yes"]:
        write_bot_file = True

if write_bot_file:
    bot_token = input("Token du bot > ")
    with open("datas/bot.json", "w") as f:
        json.dump({
            "bot_token": bot_token
        }, f)
        