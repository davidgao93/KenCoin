from asyncio import sleep
from datetime import datetime
from glob import glob

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from discord.ext.commands import Bot as BotBase
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument, CommandOnCooldown)
from discord.ext.commands import Context
from discord.errors import Forbidden, HTTPException
from discord import Intents, Embed
from discord.ext.commands.errors import CommandOnCooldown
from discord.ext.commands import when_mentioned_or

from ..db import db

PREFIX = "!"
OWNER_IDS = [863215534069776405]
COGS = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)

def get_prefix(bot, message):
	return when_mentioned_or(PREFIX)(bot, message)


class Ready(object):
	def __init__(self):
		for cog in COGS:
			setattr(self, cog, False)

	def ready_up(self, cog):
		setattr(self, cog, True)
		print(f" {cog} cog ready")

	def all_ready(self):
		return all([getattr(self, cog) for cog in COGS])

class Bot(BotBase):
	def __init__(self):
		self.PREFIX = PREFIX
		self.ready = False
		self.cogs_ready = Ready()
		self.guild = None
		self.scheduler = AsyncIOScheduler()

		db.autosave(self.scheduler)


		super().__init__(
			command_prefix=get_prefix, 
			owner_ids=OWNER_IDS,
			intents=Intents.all()
			)
	
	def setup(self):
		for cog in COGS:
			self.load_extension(f"lib.cogs.{cog}")
			print(f"  {cog} cog loaded!")

	def update_db(self):
		db.multiexec("INSERT OR IGNORE INTO guilds (GuildID) VALUES (?)", 
					((guild.id,) for guild in self.guilds))

		db.multiexec("INSERT OR IGNORE INTO ledger (UserID) VALUES (?)",
					((member.id,) for member in self.guild.members))

		stored_members = db.column("SELECT UserID FROM ledger")
		for id in stored_members:
			print(self.guild.get_member(id))

		# to_remove = []
		# stored_members = db.column("SELECT UserID FROM ledger")
		# for id_ in stored_members:
		# 	if not self.guild.get_member(id_):
		# 		to_remove.append(id_)

		# db.multiexec("DELETE FROM ledger WHERE UserID = ?",
		# 			((id_,) for id_ in to_remove))

		db.commit()

	def run(self, version):
		self.VERSION = version

		print("Running setup...")
		self.setup()

		with open("./lib/bot/token.0", "r", encoding="utf-8") as tf:
			self.TOKEN = tf.read()

		print("Starting KenCoin...")
		super().run(self.TOKEN, reconnect=True)

	# async def print_message(self):
	# 	channel = self.get_channel(699690514051629089)
	# 	await channel.send("I am a timed notification!")

	async def on_connect(self):
		print("KenCoin online")

	async def on_disconnect(self):
		print("KenCoin offline")

	async def on_error(self, err, *args, **kwargs):
		if err == "on_command_error":
			await args[0].send("Command error.")
		else:
			await self.stdout.send("An error occured.")
		raise


	async def on_command_error(self, ctx, exc):
		if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
			pass

		elif isinstance(exc, MissingRequiredArgument):
			await ctx.send("Missing parameters.")

		elif isinstance(exc, CommandOnCooldown):
			pass
			# await ctx.send(f"Command on cooldown. Try again in {exc.retry_after:,.2f} secs.")

		elif isinstance(exc.original, HTTPException):
			pass

		elif isinstance(exc.original, Forbidden):
			await ctx.send("Permissions missing.")

		else:
			raise exc.original
		

	async def on_ready(self):
		if not self.ready:
			self.guild = self.get_guild(431301983475990528)
			#self.scheduler.add_job(self.print_message, CronTrigger(second="0,15,30,45"))
			self.stdout = self.get_channel(864691394232844294)
			self.scheduler.start()
			self.update_db()

			while not self.cogs_ready.all_ready():
				await sleep(0.5)

			print("KenCoin initialized.")
			# print(self.commands)
			self.ready = True
		else:
			print("Bot reconnected")

	async def on_message(self, message):
		if not message.author.bot:
			await self.process_commands(message)

bot = Bot()
