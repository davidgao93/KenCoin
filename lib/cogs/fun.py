from discord import Embed
from discord.ext.commands import Cog
from discord.ext.commands import command
from datetime import datetime
from aiohttp import request

class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.version = bot.VERSION

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

    @command(name="pull", aliases=["p"], brief="See a pic of a cute anime girl")
    async def waifu(self, ctx):
        URL = "https://api.waifu.pics/sfw/waifu"

        async with request("GET", URL) as response:
            if response.status == 200:
                data = await response.json()
                await ctx.send(data["url"])

            else:
                await ctx.send(f"API is down, status: {response.status}")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")


def setup(bot):
    bot.add_cog(Fun(bot))
    