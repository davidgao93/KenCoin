from discord.ext.commands import Cog

from ..db import db

class gpu(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cid = bot.CID
        self.coin = bot.COIN
        self.cs = bot.CS
        self.stdout = bot.get_channel(self.cid)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("gpu")

    @Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if (reaction.message.content.startswith("Your current GPU")):
            #print("attempting to upgrade GPU")
            coins, lvl, duel = db.record(f"SELECT {self.cs}, Level, Duel FROM ledger WHERE UserID = ?", user.id)
            tiers = ["None", "Amethyst", "Topaz", "Sapphire", "Emerald", "Ruby", "Diamond", "Dragonstone", "Onyx", "Zenyte", "Kenyte",
            "Solaryte", "Galaxyte", "Universyte", "Void"]
            costs = [0, 10, 50, 200, 500, 1000, 1500, 3000, 5000, 10000, 50000, 100000, 250000, 500000, 1000000000]
            if (lvl == 14):
                await self.bot.get_channel(self.cid).send(f"Congratulations! You are already at the max tier!")
            if (coins >= costs[lvl+1] and duel == 0):
                #print("balance sufficient, deducting...")
                #print(reaction.message.id)
                await reaction.message.delete()
                await self.bot.get_channel(self.cid).send(f"Congratulations! You have upgraded to **{tiers[lvl+1]}** tier!")
                db.execute(f"UPDATE ledger SET {self.cs} = {self.cs} - ?, Level = Level + 1 WHERE UserID = ?", costs[lvl+1], user.id)
                db.commit()
            else:
                #print("insufficient funds")
                await self.bot.get_channel(self.cid).send(f"You don't have enough {self.cs} to afford the next upgrade. Come back when you do.")
        if (reaction.message.content.startswith("Congratulations!")):
            coins, lvl, prestige, duel = db.record(f"SELECT {self.cs}, Level, Prestige, Duel FROM ledger WHERE UserID = ?", user.id)
            if (lvl == 14 and duel == 0):
                await reaction.message.delete()
                await self.bot.get_channel(self.cid).send(f"Congratulations! You are now Prestige rank **{prestige+1}**!")
                db.execute(f"UPDATE ledger SET {self.cs} = 0, Level = 0, Prestige = Prestige + 1 WHERE UserID = ?", user.id)
                db.commit()
            else:
                #print("insufficient funds")
                await self.bot.get_channel(self.cid).send(f"You're not at {tiers[14]} tier yet. Try again when you are.")

    @Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        pass

    # @Cog.listener()
    # async def on_raw_reaction_add(self, payload):
    #     pass

    # @Cog.listener()
    # async def on_raw_reaction_add(self, payload):
    #     pass

def setup(bot):
    bot.add_cog(gpu(bot))
    