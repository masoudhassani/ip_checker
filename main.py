import subprocess
import smtplib
from email.mime.text import MIMEText
import datetime
import os.path
import yaml
import logging
import sys
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

def connect_type(word_list):
    """ This function takes a list of words, then, depeding which key word, returns the corresponding
    internet connection type as a string. ie) 'ethernet'.
    """
    if 'wlan0' in word_list or 'wlan1' in word_list:
        con_type = 'wifi'
    elif 'eth0' in word_list:
        con_type = 'ethernet'
    else:
        con_type = 'current'

    return con_type

def ip_change(current_ip):
    #if os.path.isfile('last_ip.txt'):
    if os.path.exists('last_ip.txt'):
        file_ip = open('last_ip.txt', 'w+')
        last_ip = file_ip.read()
        if current_ip == last_ip:
            file_ip.close()
            return False
        else:
            file_ip.write(current_ip)
            file_ip.close()            
            return True 

    else:
        file_ip = open('last_ip.txt', 'w')
        file_ip.write(current_ip)
        file_ip.close()
        return True

arg='ip route list'  # Linux command to retrieve ip addresses.
# Runs 'arg' in a 'hidden terminal'.
p=subprocess.Popen(arg,shell=True,stdout=subprocess.PIPE)
data = p.communicate()  # Get data from 'p terminal'.
print(data)
# Split IP text block into three, and divide the two containing IPs into words.
ip_lines = data[0].splitlines()
split_line_a = ip_lines[1].split()
#split_line_b = ip_lines[2].split()

# con_type variables for the message text. ex) 'ethernet', 'wifi', etc.
ip_type_a = connect_type(split_line_a)
#ip_type_b = connect_type(split_line_b)

"""Because the text 'src' is always followed by an ip address,
we can use the 'index' function to find 'src' and add one to
get the index position of our ip.
"""
ipaddr_a = split_line_a[split_line_a.index('src')+1]
#ipaddr_b = split_line_b[split_line_b.index('src')+1]

# save the ip in a text file
ip_changed = ip_change(ipaddr_a)

# Creates a sentence for each ip address.
my_ip_a = 'Your %s ip is %s' % (ip_type_a, ipaddr_a)
#my_ip_b = 'Your %s ip is %s' % (ip_type_b, ipaddr_b)

# Creates the text, subject, 'from', and 'to' of the message.
if ip_change:
    if use_email:
        now = datetime.now().strftime("%d.%b %Y %H:%M:%S")
        logging.info(f'[{now}] sending an email')

        try:
            msg = MIMEText(now + '\t' + my_ip_a + "\n")# + my_ip_b)
            msg['Subject'] = 'Change in public IP %s' % today.strftime('%b %d %Y')
            msg['From'] = gmail_user
            msg['To'] = email
            # Sends the message
            smtpserver.sendmail(gmail_user, [email], msg.as_string())
            # Closes the smtp server.
            smtpserver.quit()
        
        except Exception as e:
            logging.error(f'[{now}] error sending an email \n {e}')

    if use_telegram:
        now = datetime.now().strftime("%d.%b %Y %H:%M:%S")
        message = f'[{now}] your public ip has changed to {my_ip_a}'
        try:
            telegram_bot.send(message)
        except Exception as e:
            logging.error(f'[{now}] error in telegram bot \n {e}')
