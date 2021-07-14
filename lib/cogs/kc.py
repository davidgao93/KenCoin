from datetime import datetime, timedelta
import time
from random import randint, choice
from typing import Optional

from discord import Member
from discord.ext.commands import Cog, BucketType
from discord.ext.commands import CheckFailure
from discord.ext.commands import BadArgument
from discord.ext.commands import command, cooldown, has_permissions
from discord.ext.commands.errors import CommandOnCooldown
from discord.errors import Forbidden, HTTPException

from ..db import db

class Kencoin(Cog):
    def __init__(self, bot):
        self.bot = bot

    async def process_kc(self, message):
        coins, lvl, kclock = db.record("SELECT KC, Level, KCLock FROM ledger WHERE UserID = ?", message.author.id)

        if datetime.utcnow() > datetime.fromisoformat(kclock):
            await self.add_kc(message, coins, lvl)
        else:
            diff = datetime.fromisoformat(kclock) - datetime.utcnow()
            print(diff.seconds)
            timer = time.strftime("%Hh%Mmin", time.gmtime(diff.seconds))
            await message.send(f"{timer} until your next claim. Your balance is: {coins:,}KC.")

    async def add_kc(self, message, coins, lvl):
        coins_to_add = randint(1, 3)
        
        db.execute("UPDATE ledger SET KC = KC + ?, Level = ?, KCLock = ? WHERE UserID = ?", 
                    coins_to_add, lvl, (datetime.utcnow()+timedelta(seconds=3600)).isoformat(), message.author.id)
        await message.send(f"KC claimed! Your balance is now: {coins+coins_to_add:,}KC.")

    # async def update_nick(self, ctx, coins):
    #     new_nick = ctx.author.nick + f" ({coins}KC)"
    #     print(new_nick)
    #     await ctx.author.edit(nick=new_nick)
    #     await ctx.send(f"Values updated.")
    #     print("Nick changed")

    @command(name="claim", aliases=["c"], brief="Claim a daily amount of KC")
    # @cooldown(1, 3600, BucketType.user)
    async def claim_kc(self, ctx):
        await self.process_kc(ctx)

    @claim_kc.error
    async def claim_kc_error(self, ctx, exc):
        if isinstance(exc, CommandOnCooldown):
            timer = time.strftime("%Hh%Mmin", time.gmtime(exc.retry_after))
            await ctx.send(f"You've already claimed today. Try again in **{timer}**.")

    # @command(name="test")
    # async def test(self, ctx, member: Member, nick):
    #     await member.edit(nick=nick)
    #     await ctx.send(f'Nickname was changed for {member.mention} ')

    @command(name="wallet", aliases=["w"], brief="Check your current balance")
    async def display_wallet(self, ctx, target: Optional[Member]):
        target = target or ctx.author

        coins, lvl = db.record("SELECT KC, Level FROM ledger WHERE UserID = ?", target.id) or (None, None)

        if coins is not None: 
            await ctx.send(f"{target.display_name}'s current balance: {coins:,}KC.")
            #await self.update_nick(ctx, coins)
        else:
            await ctx.send(f"{target.display_name}'s wallet not found.")
        

    @command(name="rank", aliases=["r"], brief="Check your rank")
    async def display_rank(self, ctx, target: Optional[Member]):
        target = target or ctx.author

        ids = db.column("SELECT UserID FROM ledger ORDER BY KC DESC")

        await ctx.send(f"{target.display_name} is rank {ids.index(target.id)+1} of {len(ids)}")

    @command(name="gamba", aliases=["g"], brief="Gamble <KC>, use <all> to gamble all.")
    @cooldown(1, 5, BucketType.user)
    async def roll_dice(self, ctx, kc: str):
        coins, lvl = db.record("SELECT KC, Level FROM ledger WHERE UserID = ?", ctx.author.id)
        jackpot, amt = db.record("SELECT Jackpot, Amount FROM jackpot WHERE Jackpot = 0")
        if (kc == "all"):
            gamba_amt = coins
        else:
            gamba_amt = int(kc)

        if (gamba_amt > coins):
            await ctx.send("You don't have enough KC!")
            return

        rolls = [randint(1, 6) for i in range(5)]
        house_rolls = [randint(1, 6) for i in range(5)]
        roll_msg = " + ".join([str(r) for r in rolls]) + f" = **{sum(rolls)}**"
        house_roll_msg = " + ".join([str(r) for r in house_rolls]) + f" = **{sum(house_rolls)}**"
        await ctx.send(f"You roll the following: " + roll_msg)
        await ctx.send("The house rolls: " + house_roll_msg)
        
        if sum(rolls) == sum(house_rolls):
            await ctx.send(f"It's a **tie!** Your balance remains: {coins:,}KC.")
        elif sum(rolls) < sum(house_rolls):
            db.execute("UPDATE ledger SET KC = KC - ? WHERE UserID = ?", gamba_amt, ctx.author.id)
            db.execute("UPDATE jackpot SET Amount = Amount + ? WHERE Jackpot = 0", gamba_amt)
            await ctx.send(f"You **lose!** Your balance is now: {coins-gamba_amt:,}KC. The KC are added to the pot valued at: *{amt+gamba_amt:,}KC*.")
        elif sum(rolls) == 30:
            new_bal = coins + amt
            db.execute("UPDATE ledger SET KC = ? WHERE UserID = ?", new_bal, ctx.author.id)
            db.execute("UPDATE jackpot SET Amount = 0 WHERE Jackpot = 0")
            await ctx.send(f"**J A C K P O T** You win the Jackpot! Your balance is now: {new_bal:,}KC. The pot is now reset.")
        else:
            db.execute("UPDATE ledger SET KC = KC + ? WHERE UserID = ?", gamba_amt, ctx.author.id)
            await ctx.send(f"You **win!** Your balance is now: {coins+gamba_amt:,}KC.")

        db.commit()

    @roll_dice.error
    async def roll_dice_error(self, ctx, exc):
        if isinstance(exc, HTTPException):
            await ctx.send("Too many dice rolled, use a lower number.")

        elif isinstance(exc, BadArgument):
            await ctx.send("Bad parameters.")

        elif isinstance(exc, CommandOnCooldown):
            timer = time.strftime("%Ss", time.gmtime(exc.retry_after))[1:]
            await ctx.send(f"In efforts to prevent addiction, try again in **{timer}**.")

    @command(name="slap", aliases=["s"], brief="Slaps [user] and attempts to steal their KC")
    @cooldown(1, 3600, BucketType.user)
    async def slap_member(self, ctx, member: Member, *, reason: Optional[str] = "no reason"):

        if member == ctx.author:
            await ctx.send("Now why the hell would you want to do that?")
            return

        coins, lvl = db.record("SELECT KC, Level FROM ledger WHERE UserID = ?", member.id)
        if (coins <= 3):
            await ctx.send("This person has almost no coins, so you spare them... for now.")
            return

        rand_int = randint(0, 10)
        tribute = randint(1, 3)
        fail = [
            "As you reach forward, you suddenly get a cramp and are unable to finish the slap",
            "You slip on a pebble",
            "They were too agile and evade your slap"]

        success = [
            "They grovel at your feet",
            "They run away crying",
            "They commit sudoku"
        ]

        if (rand_int >= 5):
            db.execute("UPDATE ledger SET KC = KC + ? WHERE UserID = ?", tribute, ctx.author.id)
            db.execute("UPDATE ledger SET KC = KC - ? WHERE UserID = ?", tribute, member.id)
            db.commit()
            await ctx.send(f"{ctx.author.display_name} slapped {member.mention} for {reason}! " +
            f"{choice((success[0], success[1], success[2]))}, dropping {tribute} KenCoin(s) that {ctx.author.display_name} picks up!")
        else:
            await ctx.send(f"{choice((fail[0], fail[1], fail[2]))}!")

    @slap_member.error
    async def slap_member_error(self, ctx, exc):
        if isinstance(exc, BadArgument):
            await ctx.send("Member does not exist.")

        elif isinstance(exc, CommandOnCooldown):
            timer = time.strftime("%Mmin", time.gmtime(exc.retry_after))
            await ctx.send(f"Your arms are too tired to slap right now. Try again in **{timer}**.")


    @command(name="tip", aliases=["t"], brief="Tips [user] and give them a KC")
    @cooldown(1, 3600, BucketType.user)
    async def tip_member(self, ctx, member: Member, *, reason: Optional[str] = "no reason"):

        if member == ctx.author:
            await ctx.send("That wouldn't do much now, would it?")
            return

        coins, lvl = db.record("SELECT KC, Level FROM ledger WHERE UserID = ?", ctx.author.id)
        if (coins <= 0):
            await ctx.send("You can't tip coins that you don't own.")
            return

        db.execute("UPDATE ledger SET KC = KC - ? WHERE UserID = ?", 1, ctx.author.id)
        db.execute("UPDATE ledger SET KC = KC + ? WHERE UserID = ?", 1, member.id)
        db.commit()
        await ctx.send(f"{ctx.author.display_name} gives {member.mention} just the tip! The reason? {reason}! " +
        f"{member.display_name} graciously accepts.")

    @slap_member.error
    async def slap_member_error(self, ctx, exc):
        if isinstance(exc, BadArgument):
            await ctx.send("Member does not exist.")

        elif isinstance(exc, CommandOnCooldown):
            timer = time.strftime("%Mmin", time.gmtime(exc.retry_after))
            await ctx.send(f"Your arms are too tired to slap right now. Try again in **{timer}**.")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("kc")

    @Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            pass
            #await self.process_kc(message)


def setup(bot):
    bot.add_cog(Kencoin(bot))