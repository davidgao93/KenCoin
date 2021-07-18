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
        fields = [("New command !g rr <amt> <bullets>", "Loads a 6 chamber revolver with 1-5 bullets. Has a base multiplier MULTIPLIED by an additional 5%!", False),
        ("Gamble changes", "Gambles will now reward bonus dice in multiples of 10, with more bonus dice awarded per multiple of 10KC gambled.", False),
        ("Buff to !slap", "Can now slap anyone with a positive KC value (you must also have 1 KC), they no longer cost KC, but the CD has increased.", False),
        ("!u", "Upgrade your graphics card to mine KC in the background while you do other stuff!", False)]
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
    