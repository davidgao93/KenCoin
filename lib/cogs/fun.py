from discord import Embed
from discord.ext.commands import Cog
from discord.ext.commands import command
from datetime import datetime
# from aiohttp import request

class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.version = bot.VERSION
        self.coin = bot.COIN
        self.cs = bot.CS
        self.prefix = "$"
    @command(name="version", aliases=["v"], brief="See updates")
    async def say_version(self, ctx):
        embed = Embed(title=self.coin, description=f"Update __{self.version}__",
        colour=0x783729, timestamp=datetime.utcnow())
        fields = [(f"New Prefix", f"Prefix is now set to $ instead of !", False),
        ("Gamble nerfs", f"Gambles are now capped at 10 gambles per hour for regular gamble, roulette has no limit but cannot hit jackpot table. RR multiplier has decreased.", False),
        (f"Buff to {self.prefix}tip", f"Can now tip anyone (you must have 1{self.cs}) every 30m instead of 60m.", False),
        (f"{self.prefix}u", f"4 new tiers of GPU have been added, Solar, Galaxy, Universe, Void.", False)]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        embed.set_footer(text=f"Version {self.version}")
        await ctx.send(embed=embed)

    # @command(name="pull", aliases=["p"], brief="See a pic of a cute anime girl")
    # async def waifu(self, ctx):
    #     URL = "https://api.waifu.pics/sfw/waifu"

    #     async with request("GET", URL) as response:
    #         if response.status == 200:
    #             data = await response.json()
    #             await ctx.send(data["url"])

    #         else:
    #             await ctx.send(f"API is down, status: {response.status}")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")


def setup(bot):
    bot.add_cog(Fun(bot))
    