This script detects the public ip and sends an email or a telegram message is the ip has changed

# installation
```
pip install -r requirements.txt
```

# how to use
rename ```configs_template.yml``` to ```configs.yml``` <br />
provide the required data for the email or telegram bot <br />
run ```main.py```

# set up cron
open the cron editor
```
crontab -e
```
and add the following at the end of the file
```
*/10 * * * * cd ~/ip_checker;/user/bin/pythonX.Y ~/ip_checker/main.py
```
This will run the ip checker script every 10 minutes