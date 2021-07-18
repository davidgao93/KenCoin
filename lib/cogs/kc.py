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

class Kencoin(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.auto_print()
        self.scheduler.start()

    def mine_kc(self):
        ids = db.column("SELECT UserID FROM ledger ORDER BY Level DESC")

        for uid in ids:
            coins, lvl = db.record("SELECT KC, Level FROM ledger WHERE UserID = ?", uid)
            if (lvl != 0 and not None):
                mine_amt = lvl * randint(1, 6)
                print(f"{uid} mined {mine_amt} coins")
                db.execute("UPDATE ledger SET Mined = Mined + ? WHERE UserID = ?", mine_amt, uid)
                db.commit()
    def auto_print(self):
        # self.scheduler.add_job(self.mine_kc, CronTrigger(second="0, 15, 30, 45"))
        self.scheduler.add_job(self.mine_kc, CronTrigger(hour="*"))
    async def process_kc(self, message):
        coins, lvl, kclock, kc_mined = db.record("SELECT KC, Level, KCLock, Mined FROM ledger WHERE UserID = ?", message.author.id)

        if datetime.utcnow() > datetime.fromisoformat(kclock):
            await self.add_kc(message, coins, lvl, kc_mined)
        else:
            diff = datetime.fromisoformat(kclock) - datetime.utcnow()
            timer = time.strftime("%Hh%Mmin", time.gmtime(diff.seconds))
            await message.send(f"Claim periods are every 3 hours, on the hour. There is **{timer}** until your next claim.")

    async def add_kc(self, message, coins, lvl, kc_mined):
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

        db.execute("UPDATE ledger SET KC = KC + ?, Level = ?, KCLock = ? WHERE UserID = ?", 
                    coins_to_add, lvl, next_claim, message.author.id)
        embed = Embed(title="⛏️ You check your mining progress... ⛏️",
        colour=0x783729, timestamp=datetime.utcnow())
        embed.set_footer(text=f"Next claim is in {timer}")
        if (coins_to_add == 1):
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/699690514051629089/866085879394467871/Coins_1.png")
            embed.add_field(name="Oof, you only manage to get a **single** KC!",
            value=f"Your balance is now: **{coins+coins_to_add:,}**KC.",
            inline="False")
        elif (coins_to_add < 6):
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/699690514051629089/866086342014402620/Coins_3.png")
            embed.add_field(name=f"You mined **{coins_to_add}**KC!",
            value=f"Your balance is now: **{coins+coins_to_add:,}**KC.",
            inline="False")
        else:
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/699690514051629089/866086482641289268/Coins_1000.png")
            embed.add_field(name=f"What luck! You mined **{coins_to_add}**KC!",
            value=f"Your balance is now: **{coins+coins_to_add:,}**KC.",
            inline="False")

        tiers = ["None", "Amethyst", "Topaz", "Sapphire", "Emerald", "Ruby", "Diamond", "Dragonstone", "Onyx", "Zenyte", "Kenyte"]
        gpu_tier = tiers[int(lvl)]
        if (gpu_tier == "None"):
            embed.add_field(
                name=f"You currently don't have an upgraded GPU!",
                value=f"Purchase an upgraded GPU with KC using the !upgrade command.",
                inline=False
            )
        else:
            embed.add_field(
                name=f"Your GPU tier is currently: {gpu_tier}",
                value=f"Mining a total of {kc_mined} since your last claim. They are added to your balance.",
                inline=False)

            db.execute("UPDATE ledger SET KC = KC + ?, Mined = 0 WHERE UserID = ?", 
                kc_mined, message.author.id)
                

        await message.send(embed=embed)

    @command(name="claim", aliases=["c"], brief="Claim a daily amount of KC")
    async def claim_kc(self, ctx):
        await self.process_kc(ctx)

    @command(name="upgrade", aliases=["u"], brief="Upgrade your graphics card")
    async def upgrade(self, ctx):
        coins, lvl = db.record("SELECT KC, Level FROM ledger WHERE UserID = ?", ctx.author.id)
        tiers = ["None", "Amethyst", "Topaz", "Sapphire", "Emerald", "Ruby", "Diamond", "Dragonstone", "Onyx", "Zenyte", "Kenyte"]
        costs = [0, 10, 50, 200, 500, 1000, 1500, 3000, 5000, 10000, 50000]
        if (lvl == 0):
            await ctx.send(f"Your current GPU is not upgraded. Upgrading will cost **10**KC. React with any emoji to proceed.")
        elif (lvl == 10):
            await ctx.send(f"You have the best GPU KC can buy, Kenyte tier. There are no more upgrades possible for now.")
        else:
            await ctx.send(f"Your current GPU is {tiers[lvl]} tier. Upgrading will cost **{costs[lvl+1]}**KC. React with any emoji to proceed.")

    # @claim_kc.error
    # async def claim_kc_error(self, ctx, exc):
    #     if isinstance(exc, CommandOnCooldown):
    #         timer = time.strftime("%Hh%Mmin", time.gmtime(exc.retry_after))
    #         await ctx.send(f"You've already claimed today. Try again in **{timer}**.")

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
        

    @command(name="rank", aliases=["r"], brief="Check current rankings")
    async def display_rank(self, ctx, target: Optional[Member]):
        target = target or ctx.author

        ids = db.column("SELECT UserID FROM ledger ORDER BY KC DESC")
        embed = Embed(title="Ranking", description=f"Here is the current leaderboard:",
        colour=0x783729, timestamp=datetime.utcnow())
        index = 1
        for someid in ids:
            coins = db.record("SELECT KC FROM ledger WHERE UserID = ?", someid) or (None)
            #{ctx.bot.get_user(someid).display_name}
            #f'Balance: **{coins:,}**KC'
            if (coins is not None):
                coins_str = str(coins)
                display_name = f"{ctx.bot.get_user(someid).display_name}"
                embed.add_field(
                    name=f"Rank {index}: {display_name}", 
                    value=f"Balance: **{coins_str[1:-2]}**KC", 
                    inline=False)

            if index == 5:
                break
            else:
                index += 1
        embed.set_footer(text=f"{target.display_name} is rank {ids.index(target.id)+1} of {len(ids)}")
        await ctx.send(embed=embed)

        # await ctx.send(f"{target.display_name} is rank {ids.index(target.id)+1} of {len(ids)}")

    async def roulette(self, ctx, coins, rrkc, bullets):
        if (rrkc == "all"):
            gamba_amt = int(coins)
        elif (rrkc == 0): 
            await ctx.send("Pointless!")
            return
        else:
            if rrkc is not None:
                gamba_amt = int(rrkc)
            else:
                await ctx.send("Missing wager amount.")
                return

        if (gamba_amt > coins):
            await ctx.send("You don't have enough KC!")
            return

        if (bullets is None):
            await ctx.send("Missing bullets parameter.")
            return

        if (bullets >= 6):
            await ctx.send("A guaranteed death is just not that interesting.")
        elif (bullets < 1):
            await ctx.send("The chamber cannot be empty.")
        else:
            embed = Embed(title="🔫 Russian Roulette 🔫 ",
            colour=0x783729, timestamp=datetime.utcnow())
            embed.set_footer(text=f"Please gamble responsibly")

            roll = randint(0, 120)
            if roll >= 20 * bullets:
                multiplier = (6/(6-bullets))*1.1
                award = int(gamba_amt * multiplier)
                embed.add_field(name="You cock the trigger and pull...", value="🎊 It doesn't fire! 🎊", inline=False)
                embed.add_field(name=f"You win **{award}**KC.", value=f"Your balance is now **{coins+award-gamba_amt}**KC.", inline=False)
                db.execute("UPDATE ledger SET KC = KC + ? WHERE UserID = ?", award-gamba_amt, ctx.author.id)
            else:
                embed.add_field(name="You cock the trigger and pull...", value="💀 Oh dear, you are dead! 💀", inline=False)
                embed.add_field(name=f"You lose **{rrkc}**KC.", value=f"Your balance is now **{coins-gamba_amt}**KC, it's added to the pot.", inline=False)
                db.execute("UPDATE ledger SET KC = KC - ? WHERE UserID = ?", gamba_amt, ctx.author.id)
                db.execute("UPDATE jackpot SET Amount = Amount + ? WHERE Jackpot = 0", gamba_amt)
            await ctx.send(embed=embed)
            db.commit()


    @command(name="gamba", aliases=["g"], brief="Gamble <KC>, use <rr> <amt>/<all> for Russian Roulette, <all> to gamble all.")
    @cooldown(1, 3, BucketType.user)
    async def roll_dice(self, ctx, kc: str, rrkc: Optional[str], bullets: Optional[int]):
        coins, lvl = db.record("SELECT KC, Level FROM ledger WHERE UserID = ?", ctx.author.id) # both, unsued lvl so can be int instead of tuple
        jackpot, amt = db.record("SELECT Jackpot, Amount FROM jackpot WHERE Jackpot = 0") # same here
        if (kc == "all"):
            gamba_amt = coins
        elif (kc == "rr"):
            await self.roulette(ctx, coins, rrkc, bullets)
            return
        else:
            gamba_amt = int(kc)

        if (gamba_amt > coins):
            await ctx.send("You don't have enough KC!")
            return
        elif (gamba_amt == 0):
            await ctx.send("Pointless!")
            return
        embed = Embed(title="Gamble",
        colour=0x783729, timestamp=datetime.utcnow())
        embed.set_footer(text=f"Please gamble responsibly")
        
        rolls = [randint(1, 6) for i in range(5)]
        house_rolls = [randint(1, 6) for i in range(5)]
        roll_msg = " + ".join([str(r) for r in rolls]) + f" = **{sum(rolls)}**"
        house_roll_msg = " + ".join([str(r) for r in house_rolls]) + f" = **{sum(house_rolls)}**"
        embed.add_field(name="You roll the following", value=roll_msg, inline=False)
        embed.add_field(name="The 🤖 rolls", value=house_roll_msg, inline=False)

        if sum(rolls) == sum(house_rolls):
            embed.add_field(name="It's a 🙈 **tie!** 🙈", value=f"Your balance remains: {coins:,}KC.", inline=False)
        elif sum(rolls) < sum(house_rolls):
            db.execute("UPDATE ledger SET KC = KC - ? WHERE UserID = ?", gamba_amt, ctx.author.id)
            db.execute("UPDATE jackpot SET Amount = Amount + ? WHERE Jackpot = 0", gamba_amt)
            embed.add_field(name="🎲 You **lose!** 🎲", 
            value=f"Your balance is now: {coins-gamba_amt:,}KC. The KC are added to the pot valued at: *{amt+gamba_amt:,}KC*.",
            inline=False)
        elif sum(rolls) == 30:
            new_bal = coins + amt
            db.execute("UPDATE ledger SET KC = ? WHERE UserID = ?", new_bal, ctx.author.id)
            db.execute("UPDATE jackpot SET Amount = 0 WHERE Jackpot = 0")
            embed.add_field(name="🎰 J A C K P O T 🎰", 
            value=f"Your balance is now: {new_bal:,}KC. The pot is now **reset**.",
            inline=False)
        else:
            bonus_dice = int((gamba_amt / 10) + ((gamba_amt / 10) * 0.2))
            bonus_kc = [randint(1,6) for i in range(bonus_dice)]
            bonus_multiplier = gamba_amt/10*0.05
            bonus_total = int((sum(bonus_kc)+sum(bonus_kc)*bonus_multiplier))
            if (bonus_dice > 0):
                bonus_msg = " + ".join([str(r) for r in bonus_kc]) + f" = {sum(bonus_kc)} x bonus = **{bonus_total}**KC awarded! Your new balance is **{gamba_amt+bonus_total+coins:,}**KC."
                embed.add_field(name="🎉 You **win!** 🎉", 
                value=f"Your balance is now: {coins+gamba_amt:,}KC.",
                inline=False)
                embed.add_field(name=f"You receive **{bonus_dice}** bonus dice for betting big. You roll the following:",
                value=bonus_msg,
                inline=False)
                db.execute("UPDATE ledger SET KC = KC + ? WHERE UserID = ?", gamba_amt+bonus_total, ctx.author.id)
            else:
                embed.add_field(name="🎉 You **win!** 🎉", 
                value=f"Your balance is now: {coins+gamba_amt:,}KC.",
                inline=False)
                db.execute("UPDATE ledger SET KC = KC + ? WHERE UserID = ?", gamba_amt, ctx.author.id)

        await ctx.send(embed=embed)
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
    @cooldown(1, 7200, BucketType.user)
    async def slap_member(self, ctx, member: Member, *, reason: Optional[str] = "being a weeb"):
        
        if member == ctx.author:
            await ctx.send("Now why the hell would you want to do that?")
            return
        author_coins, author_lvl = db.record("SELECT KC, Level FROM ledger WHERE UserID = ?", ctx.author.id)
        target_coins, target_lvl = db.record("SELECT KC, Level FROM ledger WHERE UserID = ?", member.id)

        if (author_coins < 1):
            await ctx.send(f"You don't have the moral high ground to slap {member.display_name}! Try again when you have some KC.")
            return

        if (target_coins == 0):
            await ctx.send(f"As you raise your hand, you stop because you feel bad for {member.display_name} because of how broke they are.")
            return
        elif (target_coins <= 3):
            tribute = randint(1, target_coins)
        else:
            tribute = randint(1, 3)

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

        if (rand_int >= 25):
            db.execute("UPDATE ledger SET KC = KC + ? WHERE UserID = ?", tribute - 1, ctx.author.id)
            db.execute("UPDATE ledger SET KC = KC - ? WHERE UserID = ?", tribute, member.id)
            hit_msg = choice(success)
            await ctx.send(f"{ctx.author.display_name} slapped {member.mention} for {reason}! " +
            f"{hit_msg}, dropping **{tribute}**KC that {ctx.author.display_name} pockets!")
        else:
            hit_msg = choice(fail)
            db.execute("UPDATE ledger SET KC = KC - 1 WHERE UserID = ?", ctx.author.id)
            await ctx.send(f"{hit_msg}!")
        db.commit()
    @slap_member.error
    async def slap_member_error(self, ctx, exc):
        if isinstance(exc, BadArgument):
            await ctx.send("You slap the air, this makes you really tired for some reason.")

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

    @tip_member.error
    async def slap_member_error(self, ctx, exc):
        if isinstance(exc, BadArgument):
            await ctx.send("You try to tip, but it seems there's nobody there.")

        elif isinstance(exc, CommandOnCooldown):
            timer = time.strftime("%Mmin", time.gmtime(exc.retry_after))
            await ctx.send(f"You're being too generous. Please try again in **{timer}**.")

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