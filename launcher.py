from lib.bot import bot

VERSION = "0.0.4"
GID = 431301983475990528
CID = 864691394232844294

bot.run(VERSION, GID, CID)

# ps -ef | grep python3
# nohup python3 launcher.py