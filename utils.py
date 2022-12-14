import ipaddress
import os


def is_ipv4(string):
    try:
        ipaddress.IPv4Network(string)
        return True
    except ValueError:
        return False


def ip_change(current_ip):
    # if os.path.isfile('last_ip.txt'):
    if os.path.exists("last_ip.txt"):
        file_ip = open("last_ip.txt", "r+")
        last_ip = file_ip.read()
        file_ip.close()

        if current_ip == last_ip:
            return False

        else:
            file_ip = open("last_ip.txt", "w")
            file_ip.write(current_ip)
            file_ip.close()
            return True

    else:
        file_ip = open("last_ip.txt", "w")
        file_ip.write(current_ip)
        file_ip.close()
        return True
