from lib.bot import bot

VERSION = "0.0.5"
GID = 699690514051629086
CID = 699690514051629089
COIN = "KenCoin"
CS = "KC"

# Cute Animals Only
# GID = 431301983475990528
# CID = 864691394232844294
# COIN = "KenCoin"
# CS = "KC"

# VuTales
# GID = 431301983475990528
# CID = 864691394232844294
# COIN = "VuCoin"
# CS = "VC"

bot.run(VERSION, GID, CID, COIN, CS)

# ps -ef | grep python3
# nohup python3 launcher.py