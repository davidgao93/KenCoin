from datetime import datetime
import time
from random import randint, choice
from typing import Optional

from discord import Member, Embed
from discord.ext.commands import Cog, BucketType
from discord.ext.commands import BadArgument
from discord.ext.commands import command, cooldown
from discord.ext.commands.errors import CommandOnCooldown
from discord.errors import HTTPException
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from ..db import db

class Coin(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.auto_print()
        self.scheduler.start()
        self.cid = bot.CID
        self.gid = bot.GID
        self.coin = bot.COIN
        self.cs = bot.CS

    def mine_coin(self):
        ids = db.column("SELECT UserID FROM ledger ORDER BY Level DESC")

        for uid in ids:
            prestige, lvl  = db.record(f"SELECT Prestige, Level FROM ledger WHERE UserID = ?", uid)
            if ((lvl != 0 or prestige !=0) and not None):
                lvl = lvl if prestige == 0 else lvl+(prestige*14)
                rolls = [randint(1, 6) for i in range(lvl)]
                mine_amt = sum(rolls) * lvl
                print(f"{uid} mined {mine_amt} coins with prestige rank {prestige}")
                db.execute("UPDATE ledger SET Gambles = 10, Mined = Mined + ? WHERE UserID = ?", mine_amt, uid)
                db.commit()


    def auto_print(self):
        # self.scheduler.add_job(self.mine_coin, CronTrigger(second="0, 15, 30, 45"))
        self.scheduler.add_job(self.mine_coin, CronTrigger(hour="*"))


    async def process_coin(self, message):
        coins, lvl, mlock, coins_mined = db.record(f"SELECT {self.cs}, Level, Lock, Mined FROM ledger WHERE UserID = ?", message.author.id)

        if datetime.utcnow() > datetime.fromisoformat(mlock):
            await self.add_coin(message, coins, lvl, coins_mined)
        else:
            diff = datetime.fromisoformat(mlock) - datetime.utcnow()
            timer = time.strftime("%Hh%Mmin", time.gmtime(diff.seconds))
            await message.send(f"Claim periods are every 3 hours, on the hour. There is **{timer}** until your next claim.")

    async def add_coin(self, message, coins, lvl, coins_mined):
        coins_to_add = randint(1, 6)
        t = datetime.utcnow()
        if (t.hour % 3) != 0:
            diff = 3 - (t.hour % 3)
        else:
            diff = 3

        new_hour = (0 if (t.hour+diff) > 23 else t.hour+diff)
        new_day = (t.day if (t.hour+diff) < 23 else t.day+1)
        next_claim = t.replace(day=new_day, hour=new_hour, minute=0, second=0)
        diff = next_claim - datetime.utcnow()
        timer = time.strftime("%Hh%Mmin", time.gmtime(diff.seconds))

        db.execute(f"UPDATE ledger SET {self.cs} = {self.cs} + ?, Level = ?, Lock = ? WHERE UserID = ?", 
                    coins_to_add, lvl, next_claim, message.author.id)
        embed = Embed(title="?????? You check your mining progress... ??????",
        colour=0x783729, timestamp=datetime.utcnow())
        embed.set_footer(text=f"Next claim is in {timer}")
        if (coins_to_add == 1):
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/699690514051629089/866085879394467871/Coins_1.png")
            embed.add_field(name=f"Oof, you only manage to get a **single** {self.cs}!",
            value=f"Your balance is now: **{coins+coins_to_add:,}**{self.cs}.",
            inline="False")
        elif (coins_to_add < 6):
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/699690514051629089/866086342014402620/Coins_3.png")
            embed.add_field(name=f"You mined **{coins_to_add}**{self.cs}!",
            value=f"Your balance is now: **{coins+coins_to_add:,}**{self.cs}.",
            inline="False")
        else:
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/699690514051629089/866086482641289268/Coins_1000.png")
            embed.add_field(name=f"What luck! You mined **{coins_to_add}**{self.cs}!",
            value=f"Your balance is now: **{coins+coins_to_add:,}**{self.cs}.",
            inline="False")

        tiers = ["None", "Amethyst", "Topaz", "Sapphire", "Emerald", "Ruby", "Diamond", "Dragonstone", "Onyx", "Zenyte", "Kenyte",
            "Solaryte", "Galaxyte", "Universyte", "Void"]
        gpu_tier = tiers[int(lvl)]
        if (gpu_tier == "None" and coins_mined == 0):
            embed.add_field(
                name=f"You currently don't have an upgraded GPU!",
                value=f"Purchase an upgraded GPU with {self.cs} using the $upgrade command.",
                inline=False
            )
        else:
            embed.add_field(
                name=f"You have an upgraded GPU or a prestige rank.",
                value=f"Your GPU mined a total of {coins_mined:,} since your last claim. They are added to your balance.",
                inline=False)

            db.execute(f"UPDATE ledger SET {self.cs} = {self.cs} + ?, Mined = 0 WHERE UserID = ?", 
                coins_mined, message.author.id)
                

        await message.send(embed=embed)

    @command(name="claim", aliases=["c", "C"], brief="Check your mining progress")
    async def claim_coin(self, ctx):
        await self.process_coin(ctx)

    @command(name="upgrade", aliases=["u", "U"], brief="Upgrade your graphics card")
    async def upgrade(self, ctx):
        coins, lvl = db.record(f"SELECT {self.cs}, Level FROM ledger WHERE UserID = ?", ctx.author.id)
        tiers = ["None", "Amethyst", "Topaz", "Sapphire", "Emerald", "Ruby", "Diamond", "Dragonstone", "Onyx", "Zenyte", "Kenyte",
            "Solaryte", "Galaxyte", "Universyte", "Void"]
        costs = [0, 10, 50, 200, 500, 1000, 1500, 3000, 5000, 10000, 50000, 100000, 250000, 500000, 1000000000, 1000000000000]
        if (lvl == 0):
            await ctx.send(f"Your current GPU is not upgraded. Upgrading will cost **10**{self.cs}. React with any emoji to proceed.")
            return
        elif (lvl == 14):
            await ctx.send(f"You have the best GPU {self.cs} can buy, {tiers[lvl]} tier. There are no more upgrades possible for now.")
            return
        else:
            await ctx.send(f"Your current GPU is {tiers[lvl]} tier. Upgrading will cost **{costs[lvl+1]}**{self.cs}. React with any emoji to proceed.")
            return

    @command(name="prestige", aliases=["p", "P"], brief="Prestige your rank at max GPU tier, resetting your KC and gaining a prestige rank.")
    async def prestige(self, ctx):
        duel, lvl = db.record(f"SELECT Duel, Level FROM ledger WHERE UserID = ?", ctx.author.id)
        if (duel == 1):
            await ctx.send(f"You cannot prestige while sponsoring a duel.")
            return
        
        if (lvl == 14):
            await ctx.send(f"Congratulations! You are eligible to prestige your rank and multiply your mining bonuses! React with any emoji to proceed.")
            return
        else:
            await ctx.send(f"You are currently not eligible to prestige.")
            return
    # @claim_coin.error
    # async def claim_coin_error(self, ctx, exc):
    #     if isinstance(exc, CommandOnCooldown):
    #         timer = time.strftime("%Hh%Mmin", time.gmtime(exc.retry_after))
    #         await ctx.send(f"You've already claimed today. Try again in **{timer}**.")

    # @command(name="test")
    # async def test(self, ctx, member: Member, nick):
    #     await member.edit(nick=nick)
    #     await ctx.send(f'Nickname was changed for {member.mention} ')

    @command(name="wallet", aliases=["w", "W"], brief="Check your current balance")
    async def display_wallet(self, ctx, target: Optional[Member]):
        target = target or ctx.author

        coins, lvl = db.record(f"SELECT {self.cs}, Level FROM ledger WHERE UserID = ?", target.id) or (None, None)

        if coins is not None: 
            await ctx.send(f"{target.display_name}'s current balance: {coins:,}{self.cs}.")
            #await self.update_nick(ctx, coins)
        else:
            await ctx.send(f"{target.display_name}'s wallet not found.")
        

    @command(name="rank", aliases=["r", "R"], brief="Check current rankings")
    async def display_rank(self, ctx, target: Optional[Member]):
        target = target or ctx.author

        ids = db.column(f"SELECT UserID FROM ledger ORDER BY Prestige DESC, Level DESC, {self.cs} DESC")
        embed = Embed(title="Ranking", description=f"Here is the current leaderboard:",
        colour=0x783729, timestamp=datetime.utcnow())
        index = 1
        tiers = ["None", "Amethyst", "Topaz", "Sapphire", "Emerald", "Ruby", "Diamond", "Dragonstone", "Onyx", "Zenyte", "Kenyte",
            "Solaryte", "Galaxyte", "Universyte", "Void"]
        for someid in ids:
            coins, lvl, prestige = db.record(f"SELECT {self.cs}, Level, Prestige FROM ledger WHERE UserID = ?", someid) or (None, None)
            if (coins is not None):
                coins_str = f"{coins:,}"
                display_name = f"{ctx.bot.get_user(someid).display_name}"
                gpu_tier = f"{tiers[lvl]}" if lvl > 0 else "basic GPU"
                embed.add_field(
                    name=f"Rank {index}: {display_name} ({prestige}) - {gpu_tier}", 
                    value=f"Balance: **{coins_str}**{self.cs}", 
                    inline=False)

            if index == 5:
                break
            else:
                index += 1
        embed.set_footer(text=f"{target.display_name} is rank {ids.index(target.id)+1} of {len(ids)}")
        await ctx.send(embed=embed)

        # await ctx.send(f"{target.display_name} is rank {ids.index(target.id)+1} of {len(ids)}")

    async def roulette(self, ctx, coins, rrc, bullets):
        if (rrc == "all"):
            gamba_amt = int(coins)
        elif (int(rrc) <= 0): 
            await ctx.send("Pointless!")
            return
        else:
            if rrc is not None:
                gamba_amt = int(rrc)
            else:
                await ctx.send("Missing wager amount.")
                return

        if (gamba_amt > coins):
            await ctx.send(f"You don't have enough {self.cs}!")
            return

        if (bullets is None):
            await ctx.send("Missing bullets parameter.")
            return

        if (bullets >= 6):
            await ctx.send("A guaranteed death is just not that interesting.")
        elif (bullets < 1):
            await ctx.send("The chamber cannot be empty.")
        else:
            embed = Embed(title="???? Russian Roulette ???? ",
            colour=0x783729, timestamp=datetime.utcnow())
            embed.set_footer(text=f"Please gamble responsibly")

            roll = randint(0, 120)
            if roll >= 20 * bullets:
                multiplier = (6/(6-bullets))*0.98
                award = int(gamba_amt * multiplier)
                embed.add_field(name="You cock the trigger and pull...", value="???? It doesn't fire! ????", inline=False)
                embed.add_field(name=f"You win **{award}**{self.cs}.", value=f"Your balance is now **{coins+award-gamba_amt}**{self.cs}.", inline=False)
                db.execute(f"UPDATE ledger SET {self.cs} = {self.cs} + ? WHERE UserID = ?", award-gamba_amt, ctx.author.id)
            else:
                embed.add_field(name="You cock the trigger and pull...", value="???? Oh dear, you are dead! ????", inline=False)
                embed.add_field(name=f"You lose **{rrc}**{self.cs}.", value=f"Your balance is now **{coins-gamba_amt}**{self.cs}, it's added to the pot.", inline=False)
                db.execute(f"UPDATE ledger SET {self.cs} = {self.cs} - ? WHERE UserID = ?", gamba_amt, ctx.author.id)
                db.execute(f"UPDATE jackpot SET Amount = Amount + ? WHERE Jackpot = 0", gamba_amt)
            await ctx.send(embed=embed)
            db.commit()


    @command(name="gamba", aliases=["g", "G"], brief="Gamble <amt>, use <rr> <amt>/<all> for Russian Roulette, <all> to gamble all.")
    # @cooldown(1, 3, BucketType.user)
    async def roll_dice(self, ctx, amt: str, rrc: Optional[str], bullets: Optional[int]):
        coins, gambles, duel_active = db.record(f"SELECT {self.cs}, Gambles, Duel FROM ledger WHERE UserID = ?", ctx.author.id)
        jackpot, jackpot_amt = db.record("SELECT Jackpot, Amount FROM jackpot WHERE Jackpot = 0") #unsued jackpot to preserve number formatting

        if (duel_active == 1):
            await ctx.send(f"You have a pending duel! Please cancel your duel before proceeding.")
            return

        if (amt == "all"):
            gamba_amt = coins
        elif (amt == "rr"):
            await self.roulette(ctx, coins, rrc, bullets)
            return
        else:
            gamba_amt = int(amt)

        print(f"gambling {gamba_amt} with a balance of {coins} and {gambles} left")
        if (gamba_amt > coins):
            await ctx.send(f"You don't have enough {self.cs}!")
            return
        elif (gamba_amt > 5000000):
            await ctx.send(f"Gambles are capped at 5,000,000{self.cs}!")
            return
        elif (gamba_amt <= 0):
            await ctx.send("Pointless!")
            return

        if (gambles <= 0):
            await ctx.send("You are out of gambles. Try again next hour.")
            return

        gambles = int(gambles)
        if (gambles == 3):
            embed = Embed(title="Gamble",
            colour=0x783729, timestamp=datetime.utcnow())
            embed.set_footer(text=f"TWO GAMBLES LEFT")
        else:
            embed = Embed(title="Gamble",
            colour=0x783729, timestamp=datetime.utcnow())
            embed.set_footer(text=f"Please gamble responsibly")

        rolls = [randint(1, 6) for i in range(5)]
        if (gamba_amt >= 833333):
            reverse = int(gamba_amt / 833333)
            roll_sum = sum(rolls) - reverse
            roll_msg = (" + ".join([str(r) for r in rolls]) + f" = **{sum(rolls)}**. Wait, what's this? The gamble was rigged and knocks off **{reverse}**" +
            f" from your total, which is now **{roll_sum}**! What a scam!")
        else:
            roll_sum = sum(rolls)
            roll_msg = (" + ".join([str(r) for r in rolls]) + f" = **{roll_sum}**.")

        house_rolls = [randint(1, 6) for i in range(5)]
        house_roll_msg = " + ".join([str(r) for r in house_rolls]) + f" = **{sum(house_rolls)}**"
        embed.add_field(name="You roll the following", value=roll_msg, inline=False)
        embed.add_field(name="The ???? rolls", value=house_roll_msg, inline=False)

        if roll_sum == sum(house_rolls):
            embed.add_field(name="It's a ???? **tie!** ????", value=f"Your balance remains: {coins:,}{self.cs} and no gamble count was deducted.", inline=False)
        elif roll_sum < sum(house_rolls):
            if (coins > 100000):
                extra_loss = int(coins * 0.9)
            else:
                extra_loss = 0

            if (gamba_amt > 1000 or gamba_amt <= 0):
                jackpot_add = 1000
            else:
                jackpot_add = gamba_amt
            db.execute("UPDATE jackpot SET Amount = Amount + ? WHERE Jackpot = 0", jackpot_add)
            if (extra_loss > 0):
                embed.add_field(name="???? You **lose!** ????", 
                value=(f"Your balance is now: **{coins-gamba_amt:,}**{self.cs}. {jackpot_add:,}{self.cs} are added to the pot valued at: **{jackpot_amt+jackpot_add:,}**{self.cs}."),
                inline=False)
                if (coins-gamba_amt-extra_loss) < 0:
                    final_bal = 10000 
                    final_msg = f"As you went broke, they take pity on you and drop a bag of 10,000{self.cs} on your lap."
                    db.execute(f"UPDATE ledger SET {self.cs} = 10000, Gambles = Gambles - 1 WHERE UserID = ?", ctx.author.id)
                else:
                    final_bal = coins-gamba_amt-extra_loss
                    final_msg = f"Your new balance is: **{final_bal:,}**{self.cs}!"
                    db.execute(f"UPDATE ledger SET {self.cs} = ?, Gambles = Gambles - 1 WHERE UserID = ?", final_bal, ctx.author.id)
                embed.add_field(name="???? WEE WOO WEE WOO. UH OH! It's the rich people police! ????", 
                value=(f"They clobber you over the head, taking an additional **{extra_loss:,}**{self.cs} from you! " + final_msg),
                inline=False)
            else:
                db.execute(f"UPDATE ledger SET {self.cs} = {self.cs} - ?, Gambles = Gambles - 1 WHERE UserID = ?", gamba_amt, ctx.author.id)
                embed.add_field(name="???? You **lose!** ????", 
                value=f"Your balance is now: **{coins-gamba_amt:,}**{self.cs}. The {self.cs} are added to the pot valued at: **{jackpot_amt+jackpot_add:,}**{self.cs}.",
                inline=False)              
        elif sum(rolls) == 30:
            new_bal = coins + amt
            db.execute(f"UPDATE ledger SET {self.cs} = ?, Gambles = Gambles - 1 WHERE UserID = ?", new_bal, ctx.author.id)
            db.execute("UPDATE jackpot SET Amount = 0 WHERE Jackpot = 0")
            embed.add_field(name="???? ???? ???? J A C K P O T ???? ???? ????", 
            value=f"???????????? C O N G R A T U L A T I O N S! ???????????? Your balance is now: {new_bal:,}{self.cs}!!! The pot is now **reset**.",
            inline=False)
        else:
            bonus_dice = int((gamba_amt / 10) + ((gamba_amt / 10) * 0.2))
            bonus_amt = [randint(1,6) for i in range(bonus_dice)]
            bonus_multiplier = gamba_amt/10*0.05
            bonus_total = int((sum(bonus_amt)+sum(bonus_amt)*bonus_multiplier))
            if (bonus_dice > 0):
                if (bonus_dice < 25):
                    bonus_msg = (" + ".join([str(r) for r in bonus_amt]) + f" = {sum(bonus_amt)} x bonus = **{bonus_total:,}**{self.cs} awarded! " +
                    f"Your new balance is **{gamba_amt+bonus_total+coins:,}**{self.cs}.")
                else:
                    bonus_msg = ("Numerous bonus dice were summed for a total of:" + f" {sum(bonus_amt):,} x bonus = **{bonus_total:,}**{self.cs} awarded! " +
                    f"Your new balance is **{gamba_amt+bonus_total+coins:,}**{self.cs}.")
                embed.add_field(name="???? You **win!** ????", 
                value=f"Your balance is now: {coins+gamba_amt:,}{self.cs}.",
                inline=False)
                embed.add_field(name=f"You receive **{bonus_dice:,}** bonus dice for betting big. You roll the following:",
                value=bonus_msg,
                inline=False)
                db.execute(f"UPDATE ledger SET {self.cs} = {self.cs} + ?, Gambles = Gambles - 1 WHERE UserID = ?", gamba_amt+bonus_total, ctx.author.id)
            else:
                embed.add_field(name="???? You **win!** ????", 
                value=f"Your balance is now: {coins+gamba_amt:,}{self.cs}.",
                inline=False)
                db.execute(f"UPDATE ledger SET {self.cs} = {self.cs} + ?, Gambles = Gambles - 1 WHERE UserID = ?", gamba_amt, ctx.author.id)

        await ctx.send(embed=embed)
        db.commit()

    @roll_dice.error
    async def roll_dice_error(self, ctx, exc):
        if isinstance(exc, HTTPException):
            await ctx.send("Too many dice rolled, use a lower number.")

        elif isinstance(exc, BadArgument):
            await ctx.send("Missing a gamble amount or type of gamble.")

        elif isinstance(exc, CommandOnCooldown):
            timer = time.strftime("%Ss", time.gmtime(exc.retry_after))[1:]
            await ctx.send(f"In efforts to prevent addiction, try again in **{timer}**.")

    @command(name="slap", aliases=["s", "S"], brief="Slaps [user] and make them suffer")
    @cooldown(1, 7200, BucketType.user)
    async def slap_member(self, ctx, member: Member, *, reason: Optional[str] = "being a weeb"):
        
        if member == ctx.author:
            await ctx.send("Now why the hell would you want to do that?")
            self.slap_member.reset_cooldown(ctx)
            return
        author_coins, author_lvl = db.record(f"SELECT {self.cs}, Level FROM ledger WHERE UserID = ?", ctx.author.id)
        target_coins, target_lvl = db.record(f"SELECT {self.cs}, Level FROM ledger WHERE UserID = ?", member.id)

        if (author_coins < 1):
            await ctx.send(f"You don't have the moral high ground to slap {member.display_name}! Try again when you have some {self.cs}.")
            self.slap_member.reset_cooldown(ctx)
            return

        if (target_coins <= 5):
            await ctx.send(f"As you raise your hand, you stop because you feel bad for {member.display_name} because of how broke they are.")
            self.slap_member.reset_cooldown(ctx)
            return
        elif (target_coins <= 100):
            tribute = randint(1, 5)
        else:
            tribute = int((randint(1, 5)/100)*target_coins)
            if (tribute > 3000):
                tribute = 3000


        rand_int = randint(0, 100)
        fail = [
            "As you reach forward, you suddenly get a cramp and are unable to finish the slap",
            "You slip on a pebble",
            "They were too agile and evade your slap",
            "Divine intervention steps in and prevents you from slapping",
            "As you raise your hand, you sneeze and miss your target",
            "You trip over a wandering rattlesnake"
            ]

        success = [
            "They grovel at your feet",
            "They run away crying",
            "They commit sudoku",
            "They keel over from pain",
            "Their soul is slapped from their body"
        ]

        if (rand_int >= 10):
            db.execute(f"UPDATE ledger SET {self.cs} = {self.cs} + ? WHERE UserID = ?", tribute, ctx.author.id)
            db.execute(f"UPDATE ledger SET {self.cs} = {self.cs} - ? WHERE UserID = ?", tribute, member.id)
            hit_msg = choice(success)
            await ctx.send(f"{ctx.author.display_name} slapped {member.mention} for {reason}! " +
            f"{hit_msg}, dropping **{tribute}**{self.cs} that {ctx.author.display_name} pockets!")
        else:
            hit_msg = choice(fail)
            db.execute(f"UPDATE ledger SET {self.cs} = {self.cs} WHERE UserID = ?", ctx.author.id)
            await ctx.send(f"{hit_msg}!")
        db.commit()

    @slap_member.error
    async def slap_member_error(self, ctx, exc):
        if isinstance(exc, BadArgument):
            self.slap_member.reset_cooldown(ctx)
            await ctx.send("You slap the air, this makes you really tired for some reason.")

        elif isinstance(exc, CommandOnCooldown):
            timer = time.strftime("%Hh%Mmin", time.gmtime(exc.retry_after))
            await ctx.send(f"Your arms are too tired to slap right now. Try again in **{timer}**.")


    @command(name="tip", aliases=["t", "T"], brief="Tips <user> and give them a token of your appreciation for [reason]")
    @cooldown(1, 1800, BucketType.user)
    async def tip_member(self, ctx, member: Member, *, reason: Optional[str] = "no reason"):

        if member == ctx.author:
            await ctx.send("That wouldn't do much now, would it?")
            return

        coins, lvl = db.record(f"SELECT {self.cs}, Level FROM ledger WHERE UserID = ?", ctx.author.id)
        if (coins <= 0):
            await ctx.send("You can't tip coins that you don't own.")
            return

        db.execute(f"UPDATE ledger SET {self.cs} = {self.cs} - ? WHERE UserID = ?", 1, ctx.author.id)
        db.execute(f"UPDATE ledger SET {self.cs} = {self.cs} + ? WHERE UserID = ?", 1, member.id)
        db.commit()
        await ctx.send(f"{ctx.author.display_name} gives {member.mention} just the tip! The reason? {reason}! " +
        f"{member.display_name} graciously accepts.")

    @tip_member.error
    async def slap_member_error(self, ctx, exc):
        if isinstance(exc, BadArgument):
            await ctx.send("You try to tip, but it seems there's nobody there.")

        elif isinstance(exc, CommandOnCooldown):
            timer = time.strftime("%Mmin", time.gmtime(exc.retry_after))
            await ctx.send(f"You're being too generous. Please try again in **{timer}**.")

    # @command(name="zzz", aliases=["z", "Z"], brief="test command")
    # async def z_member(self, ctx, member: Member, *, reason: Optional[str] = "no reason"):
    #     if (ctx.author.id == 61330577730576384):
    #         db.execute(f"UPDATE ledger SET {self.cs} = 1000000000000, Level = 14 WHERE UserID = ?", ctx.author.id)
    #         db.commit()
    #     print("cmd executed")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("coin")

    # @Cog.listener()
    # async def on_message(self, message):
    #     if not message.author.bot:
    #         pass
            #await self.process_coin(message)


def setup(bot):
    bot.add_cog(Coin(bot))