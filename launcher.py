from lib.bot import bot

VERSION = "0.0.6"
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
# GID = 157344609993752577
# CID = 596214228394967080
# COIN = "VuCoin"
# CS = "VC"

# VuTales Test
# GID = 699690514051629086
# CID = 699690514051629089
# COIN = "VuCoin"
# CS = "VC"

bot.run(VERSION, GID, CID, COIN, CS)

# ps -ef | grep python3
# nohup python3 launcher.py