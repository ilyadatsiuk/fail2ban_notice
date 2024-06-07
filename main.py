import telebot
import time
import requests
import os
from telebot import types
import threading

TOKEN = 'YOUR TELEGRAM BOT TOKEN' # Put your Telegram bot token
CHAT_ID = YOUR CHAT ID # Put your chat id in telegram.
SLEEP_TIME = 60 # In seconds

FAIL2BAN_LOG_PATH = '/var/log/fail2ban.log'

PREVIOUS_BANNED_IPS_FILE = 'previous_banned_ips.txt'

bot = telebot.TeleBot(TOKEN)
@bot.message_handler(commands=['cleanup'])
def handle_cleanup(message):
    try:
       bot.reply_to(message, "List of baned IPs is baned now!") 
       cleanup_previous_banned_ips()
    except Exception as e:
        bot.reply_to(message, f"Error with erasing the list od baned IPs: {str(e)}")

def save_previous_banned_ips(ip_addresses):
    with open(PREVIOUS_BANNED_IPS_FILE, 'w') as f:
        for ip_address in ip_addresses:
            f.write(ip_address + '\n')

def send_message(message):
    bot.send_message(CHAT_ID, message)

def get_country(ip_address):
    response = requests.get(f'https://ipinfo.io/{ip_address}/json')
    data = response.json()
    country = data.get('country')
    return country

def load_previous_banned_ips():
    try:
        with open(PREVIOUS_BANNED_IPS_FILE, 'r') as f:
            return [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        return []

def check_fail2ban_log():
    previous_banned_ips = load_previous_banned_ips()
    with open(FAIL2BAN_LOG_PATH, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if 'fail2ban.actions' in line and 'Ban' in line:
                ip_address = line.split(' ')[-1].strip()
                if ip_address not in previous_banned_ips:
                    previous_banned_ips.append(ip_address)
                    save_previous_banned_ips(previous_banned_ips)
                    country = get_country(ip_address)
                    message = f"New baned IP: {ip_address}\nCountry: {country}"
                    send_message(message)

def cleanup_previous_banned_ips():
    if os.path.exists(PREVIOUS_BANNED_IPS_FILE):
        os.remove(PREVIOUS_BANNED_IPS_FILE)

def whileCheckList():
    while True:
        check_fail2ban_log()
        time.sleep(SLEEP_TIME)


thread1 = threading.Thread(target=whileCheckList, name="While Check List")

if __name__ == "__main__":
    thread1.start()

bot.polling(none_stop=True)
