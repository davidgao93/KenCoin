from random import choice, randint
						  
from typing import Optional

from discord import Member, Embed
from discord.ext.commands import Cog, BucketType
from discord.ext.commands import command, cooldown

from discord.ext.commands.errors import CommandOnCooldown


class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    # @command()
    # async def hello(self, ctx):
    #     await ctx.send(f"Hi {ctx.author.mention}")
		
    @command(name="hello", aliases=["hi"], brief="If you're lonely")
    async def say_hello(self, ctx):
        await ctx.send(f"{choice(('Hello', 'Hi', 'Hey', 'Hiya'))} {ctx.author.mention}!")


    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")


def setup(bot):
    bot.add_cog(Fun(bot))
    