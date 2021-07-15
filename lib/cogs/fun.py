from random import choice, randint
						  
from typing import Optional

from discord import Member, Embed
from discord.ext.commands import Cog, BucketType
from discord.ext.commands import command, cooldown
from datetime import datetime
from discord.ext.commands.errors import CommandOnCooldown


class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.version = bot.VERSION
    # @command()
    # async def hello(self, ctx):
    #     await ctx.send(f"Hi {ctx.author.mention}")
		
    # @command(name="hello", aliases=["hi"], brief="If you're lonely")
    # async def say_hello(self, ctx):
    #     await ctx.send(f"{choice(('Hello', 'Hi', 'Hey', 'Hiya'))} {ctx.author.mention}!")

    @command(name="version", aliases=["v"], brief="See updates")
    async def say_version(self, ctx):
        embed = Embed(title="KenCoin", description=f"Update __{self.version}__",
        colour=0x783729, timestamp=datetime.utcnow())
        fields = [("New command !version | !v", "Returns the current version and new features", False),
        ("Claim changes", "Claims are now reset on the hour, every 3 hours. Will be in effect starting after your next claim.", False),
        ("Nerf to !slap", "Slaps now cost 1 KC, but are 50% more likely to succeed than before.", False)]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        embed.set_footer(text=f"Version {self.version}")
        await ctx.send(embed=embed)


    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")


def setup(bot):
    bot.add_cog(Fun(bot))
    