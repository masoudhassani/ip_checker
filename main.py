import smtplib
from email.mime.text import MIMEText
import datetime
import os.path
import yaml
import logging
import sys
from requests import get
from modules import TelegramBot

# read configs 
with open('configs.yml','r') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

email = config['email']['email']
gmail_user = config['email']['user']
gmail_password = config['email']['password']
use_email = config['email']['active']
use_telegram = config['telegram']['active']

# logging 
logging.basicConfig(filename='logs.txt', 
                    format='%(levelname)s %(message)s', 
                    level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

# instanciate the telegram bot
if use_telegram:
    telegram_bot = TelegramBot(config=config['telegram'], logger=logging)

# create a server for email
if use_email:
    smtpserver = smtplib.SMTP_SSL('smtp.gmail.com', 465) 
    smtpserver.ehlo()  # Says 'hello' to the server
    # smtpserver.starttls()  # Start TLS encryption
    smtpserver.ehlo()
    smtpserver.login(gmail_user, gmail_password)  # Log in to server
    today = datetime.date.today()  # Get current time/date


def ip_change(current_ip):
    #if os.path.isfile('last_ip.txt'):
    if os.path.exists('last_ip.txt'):
        file_ip = open('last_ip.txt', 'r+')
        last_ip = file_ip.read()
        file_ip.close()

        if current_ip == last_ip:
            return False

        else:
            file_ip = open('last_ip.txt', 'w')
            file_ip.write(current_ip)
            file_ip.close()            
            return True 

    else:
        file_ip = open('last_ip.txt', 'w')
        file_ip.write(current_ip)
        file_ip.close()
        return True

ip = get('https://api.ipify.org').content.decode('utf8')

# save the ip in a text file
ip_changed = ip_change(ip)

# Creates the text, subject, 'from', and 'to' of the message.
if ip_changed:
    if use_email:
        now = datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S")
        logging.info(f'[{now}] Your public IP has changd to {ip}')
        logging.info(f'[{now}] sending an email')

        try:
            msg = MIMEText('[{now}] Your public IP has changd to {ip} \n')
            msg['Subject'] = 'Change in public IP'
            msg['From'] = gmail_user
            msg['To'] = email
            # Sends the message
            smtpserver.sendmail(gmail_user, [email], msg.as_string())
            # Closes the smtp server.
            smtpserver.quit()
            logging.info(f'email was sent succefully')
        
        except Exception as e:
            logging.error(f'[{now}] error sending an email \n {e}')

    if use_telegram:
        now = datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S")
        logging.info(f'[{now}] sending a telegram message')
        message = f'[{now}] Your public IP has changed to {ip}'

        try:
            telegram_bot.send(message)

        except Exception as e:
            logging.error(f'[{now}] error in telegram bot \n {e}')

# stop the telegram bot to stop the script
if use_telegram:
    telegram_bot.stop()