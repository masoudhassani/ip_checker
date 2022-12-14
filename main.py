import smtplib
from email.mime.text import MIMEText
import datetime
import yaml
import logging
import sys
import time
from requests import get
from modules import TelegramBot
from utils import *

# read configs
with open("configs.yml", "r") as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

use_email = config["email"]["active"]
use_telegram = config["telegram"]["active"]

# logging
logging.basicConfig(filename="logs.txt", format="%(levelname)s %(message)s", level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

# instanciate the telegram bot
if use_telegram:
    telegram_bot = TelegramBot(config=config["telegram"], logger=logging)

# create a server for email
if use_email:
    email = config["email"]["email"]
    gmail_user = config["email"]["user"]
    gmail_password = config["email"]["password"]

    smtpserver = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    smtpserver.ehlo()  # Says 'hello' to the server
    # smtpserver.starttls()  # Start TLS encryption
    smtpserver.ehlo()
    smtpserver.login(gmail_user, gmail_password)  # Log in to server
    today = datetime.date.today()  # Get current time/date

counter = 0
while True:
    counter += 1
    now = datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S")
    logging.info(f"[{now}] try {counter} - fetching the public ip address ...")
    ip = get("https://api.ipify.org").content.decode("utf8")
    success = is_ipv4(ip)
    if success:
        now = datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S")
        logging.info(f"[{now}] public ip address detected: {ip}")
        break

    if counter > 9:
        now = datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S")
        logging.info(f"[{now}] unable to get the ip address. exiting ...")
        sys.exit()

    time.sleep(10)

# save the ip in a text file
ip_changed = ip_change(ip)

# Creates the text, subject, 'from', and 'to' of the message.
if ip_changed:
    if use_email:
        now = datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S")
        logging.info(f"[{now}] Your public IP has changd to {ip}")
        logging.info(f"[{now}] sending an email")

        try:
            msg = MIMEText("[{now}] your public ip has changd to {ip} \n")
            msg["Subject"] = "Change in public ip"
            msg["From"] = gmail_user
            msg["To"] = email
            # Sends the message
            smtpserver.sendmail(gmail_user, [email], msg.as_string())
            # Closes the smtp server.
            smtpserver.quit()
            logging.info(f"email was sent succefully")

        except Exception as e:
            logging.error(f"[{now}] error sending an email \n {e}")

    if use_telegram:
        now = datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S")
        logging.info(f"[{now}] sending a telegram message")
        message = f"[{now}] your public ip has changed to {ip}"

        try:
            telegram_bot.send(message)

        except Exception as e:
            logging.error(f"[{now}] error in telegram bot \n {e}")

# stop the telegram bot to stop the script
if use_telegram:
    telegram_bot.stop()
