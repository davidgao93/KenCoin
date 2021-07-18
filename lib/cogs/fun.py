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

    @command(name="version", aliases=["v"], brief="See updates")
    async def say_version(self, ctx):
        embed = Embed(title=self.coin, description=f"Update __{self.version}__",
        colour=0x783729, timestamp=datetime.utcnow())
        fields = [("New command !d <amt>", f"Sets up a duel with <amt> as the ante. Anyone with enough {self.coin} can challenge.", False),
        ("Gamble changes", f"Gambles will now reward bonus dice in multiples of 10, with more bonus dice awarded per multiple of 10{self.cs} gambled.", False),
        ("Buff to !slap", f"Can now slap anyone with a positive {self.cs} value (you must also have 1{self.cs}), " + 
        f" they no longer cost {self.cs}, but the CD has increased.", False),
        ("!u", f"Upgrade your graphics card to mine {self.cs} hourly in the background while you do other stuff!", False)]
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
    