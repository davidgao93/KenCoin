from discord.ext.commands import Cog

from ..db import db

class Reactions(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cid = bot.CID
        self.stdout = bot.get_channel(self.cid)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("reactions")

    @Cog.listener()
    async def on_reaction_add(self, reaction, user):
        coins, lvl = db.record("SELECT KC, Level FROM ledger WHERE UserID = ?", user.id)
        tiers = ["None", "Amethyst", "Topaz", "Sapphire", "Emerald", "Ruby", "Diamond", "Dragonstone", "Onyx", "Zenyte", "Kenyte"]
        costs = [0, 10, 50, 200, 500, 1000, 1500, 3000, 5000, 10000, 50000]
        if (reaction.message.content.startswith("Your current GPU")):
            #print("attempting to upgrade GPU")
            if (lvl == 10):
                await self.bot.get_channel(self.cid).send(f"Congratulations! You are already at the max tier!")
            if (coins >= costs[lvl+1]):
                #print("balance sufficient, deducting...")
                await self.bot.get_channel(self.cid).send(f"Congratulations! You have upgraded to **{tiers[lvl+1]}** tier!")
                db.execute("UPDATE ledger SET KC = KC - ?, Level = Level + 1 WHERE UserID = ?", costs[lvl+1], user.id)
                db.commit()
            else:
                #print("insufficient funds")
                await self.bot.get_channel(self.cid).send("You don't have enough KC to afford the next upgrade. Come back when you do.")
            

    @Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        pass

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        pass

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        pass

def setup(bot):
    bot.add_cog(Reactions(bot))
    