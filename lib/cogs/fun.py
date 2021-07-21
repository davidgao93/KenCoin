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
    @command(name="version", aliases=["v", "V"], brief="See updates")
    async def say_version(self, ctx):
        embed = Embed(title=self.coin, description=f"Update __{self.version}__",
        colour=0x783729, timestamp=datetime.utcnow())
        fields = [(f"Slap Changes", f"Slaps now steal 1-5% of the target's balance, capped at a total of 3000{self.cs}, they are 50% more likely to succeed.", False),
        ("Rich police", f"Gambles past 100k are now penalized in success rate (roughly 10%) and have an additional 90% tax on losses.", False),
        ("$rank", f"Rankings now go by Prestige (more below) > GPU Tier > {self.cs} balance.", False),
        (f"$prestige", (f"You may now prestige your GPU tier, prestige resets your KC amount to 0 but you keep all mining bonuses, and earns you a prestige rank." +
        f" Prestige ranks multiplies your background mining rate, with a higher bonus based on your rank."), False),
        (f"Buff to bg mining", (f"GPUs now multiplicatively mine {self.cs} instead of additively, so if your GPU was T10 (Dragon), the bonus would be 10 x 6 rolls x 10"), False)]
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
    