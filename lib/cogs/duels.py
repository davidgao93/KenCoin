import re
import time
from datetime import datetime
from random import randint
from discord import Member, Embed
from asyncio import sleep

from discord.ext.commands import Cog
from discord.ext.commands import command
from discord.ext.commands import BadArgument

from ..db import db

class Duels(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cid = bot.CID
        self.gid = bot.GID
        self.coin = bot.COIN
        self.cs = bot.CS

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("duels")

    @Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if (reaction.message.content.startswith("It's a duel!")):
            coins, lvl = db.record(f"SELECT {self.cs}, Level FROM ledger WHERE UserID = ?", user.id)
            reg = re.findall('\d+', reaction.message.content)
            duel_amt = int(reg[0])
            sponsor = int(reg[1])
            sponsor_name = self.bot.get_user(sponsor).display_name
            if (user.id == sponsor):
                await reaction.message.delete()
                await self.bot.get_channel(self.cid).send(f"Duel cancelled! You are refunded {duel_amt}{self.cs}.", delete_after=5)
                db.execute(f"UPDATE ledger SET {self.cs} = {self.cs} + ? WHERE UserID = ?", duel_amt, sponsor)
                db.commit()
                return

            if (coins < duel_amt) :
                await self.bot.get_channel(self.cid).send(f"You don't have enough to match the duel amount. Try again when you do.")
            else:
                await self.bot.get_channel(self.cid).send(f"{user} has accepted the duel!", delete_after=30)
                await self.bot.get_channel(self.cid).send(f"You both pull out your abyssal whips...", delete_after=5)
                await sleep(1.5)
                print(f"dueling {user.id} and {sponsor}")
                sponsor_hp = 99
                user_hp = 99
                sponsor_roll = randint(0,100)
                user_roll = randint(0,100)
                if (sponsor_roll > user_roll):
                    PID = 1 # sponsor has PID
                    await self.bot.get_channel(self.cid).send(f"{sponsor_name} has the PID advantage! They strike first!")
                else:
                    PID = 0 # challenger has PID
                    await self.bot.get_channel(self.cid).send(f"{user} has the PID advantage! They strike first!")

                while (not (sponsor_hp <= 0 or user_hp <= 0)):
                    await sleep(4)
                    if PID == 1:
                        embed = Embed(title="⚔️ Duels ⚔️",
                            colour=0x783729)
                        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/699690514051629089/866413194285547530/Abyssal_whip.png")
                        sponsor_hit = randint(8,20) if randint(0, 100) > 20 else 0
                        user_hit = randint(8,20) if randint(0, 100) > 20 else 0
    
                        if (sponsor_hit > 0):
                            user_hp = user_hp - sponsor_hit
                            user_hp = user_hp if user_hp > 0 else 0
                            embed.add_field(name=f"💥 {sponsor_name} hits for **{sponsor_hit}** damage. 💥",
                            value=f"{user} has **{user_hp}**HP left!" if user_hp> 0 else f"You cleanly slash **{user}**'s head off with one last attack!", 
                            inline=False)
                        else:
                            embed.add_field(name=f"💨 {sponsor_name} misses! 💨",
                            value=f"{user} has **{user_hp}**HP left!", 
                            inline=False)

                        if (user_hp > 0):
                            if (user_hit > 0):
                                sponsor_hp = sponsor_hp - user_hit
                                sponsor_hp = sponsor_hp if sponsor_hp > 0 else 0
                                embed.add_field(name=f"💥 {user} hits for **{user_hit}** damage. 💥",
                                value=f"{sponsor_name} has **{sponsor_hp}**HP left!" if sponsor_hp > 0 else f"You cleanly slash **{sponsor_name}**'s head off with one last attack!", 
                                inline=False)
                            else:
                                embed.add_field(name=f"💨 {user} misses! 💨",
                                value=f"{sponsor_name} has **{sponsor_hp}**HP left!", 
                                inline=False)
                        else:
                            embed.add_field(name=f"💀 {user} is dead! 💀",
                            value=f"{sponsor_name} has won the duel with **{sponsor_hp}**HP left!", 
                            inline=False)
                        await self.bot.get_channel(self.cid).send(embed=embed, delete_after=5)
                    else:
                        embed = Embed(title="⚔️ Duels ⚔️",
                            colour=0x783729)
                        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/699690514051629089/866413194285547530/Abyssal_whip.png")
                        sponsor_hit = randint(8,20) if randint(0, 100) > 20 else 0
                        user_hit = randint(8,20) if randint(0, 100) > 20 else 0

                        if (user_hit > 0):
                            sponsor_hp = sponsor_hp - user_hit
                            sponsor_hp = sponsor_hp if sponsor_hp > 0 else 0
                            embed.add_field(name=f"💥 {user} hits for **{user_hit}** damage. 💥",
                            value=f"{sponsor_name} has **{sponsor_hp}**HP left!" if sponsor_hp > 0 else f"You brutally slash **{sponsor_name}**'s head off with one last attack!", 
                            inline=False)
                        else:
                            embed.add_field(name=f"💨 {user} misses! 💨",
                            value=f"{sponsor_name} has **{sponsor_hp}**HP left!", 
                            inline=False)
                        
                        if (sponsor_hp > 0):
                            if (sponsor_hit > 0):
                                user_hp = user_hp - sponsor_hit
                                user_hp = user_hp if user_hp > 0 else 0
                                embed.add_field(name=f"💥 {sponsor_name} hits for **{sponsor_hit}** damage. 💥",
                                value=f"{user} has **{user_hp}**HP left!" if user_hp> 0 else f"You brutally slash **{user}**'s head off with one last attack!", 
                                inline=False)
                            else:
                                embed.add_field(name=f"💨 {sponsor_name} misses! 💨",
                                value=f"{user} has **{user_hp}**HP left!", 
                                inline=False)
                        else:
                            embed.add_field(name=f"💀 {sponsor_name} is dead! 💀",
                            value=f"{user} has won the duel with **{user_hp}**HP left!", 
                            inline=False)                            

                        await self.bot.get_channel(self.cid).send(embed=embed, delete_after=5)
                embed_result = Embed(title="⚔️ Duel result ⚔️",
                colour=0x783729, timestamp=datetime.utcnow())
                embed_result.set_footer(text=f"We look forward to your next duel")
                embed_result.set_thumbnail(url="https://cdn.discordapp.com/attachments/699690514051629089/866413194285547530/Abyssal_whip.png")
                if (sponsor_hp == 0): # Sponsor loses, no need to remove money twice
                    embed_result.add_field(name=f"🎉 {user} wins {duel_amt * 2}{self.cs}. 🎉",
                                value=f"{sponsor_name} hangs their head in shame.", 
                                inline=False)
                    db.execute(f"UPDATE ledger SET {self.cs} = {self.cs} + ? WHERE UserID = ?", duel_amt * 2, user.id)
                else: # Sponsor wins, get duel_amt * 2, user loses
                    embed_result.add_field(name=f"🎉 {sponsor_name} wins {duel_amt * 2}{self.cs}. 🎉",
                                value=f"{user} hangs their head in shame.", 
                                inline=False)
                    db.execute(f"UPDATE ledger SET {self.cs} = {self.cs} + ? WHERE UserID = ?", duel_amt * 2, sponsor)                          
                    db.execute(f"UPDATE ledger SET {self.cs} = {self.cs} - ? WHERE UserID = ?", duel_amt, user.id)    
                await self.bot.get_channel(self.cid).send(embed=embed_result)
                await reaction.message.delete()
                db.commit()
            
    @command(name="duel", aliases=["d"], brief=f"Start a duel with <amt> as the ante.")
    async def set_duel(self, ctx, amt: int):
        coins, lvl = db.record(f"SELECT {self.cs}, Level FROM ledger WHERE UserID = ?", ctx.author.id) # both, unsued lvl so can be int instead of tuple

        if (amt > coins):
            await ctx.send(f"You don't have enough {self.cs} to start this duel.")
            return
        elif (amt == 0):
            await ctx.send("Killing each other is fun and all, but there needs to be a stake.")
            return

        embed = Embed(title="⚔️ Duels ⚔️",
        colour=0x783729, timestamp=datetime.utcnow())
        embed.set_footer(text=f"Please duel responsibly")
        embed.add_field(name=f"You put down **{amt}**{self.cs}.",
         value=f"Your new balance is **{coins - amt}**{self.cs}", 
         inline=False)
        await ctx.send(embed=embed)
        await ctx.send(f"It's a duel! {ctx.author.name} has sponsored a duel for **{amt}**{self.cs}! React to **this message** to fight to the death!" +
                    f"*You may cancel the duel as the sponsor by reacting to get your {self.cs} back.* Duel ID: {ctx.author.id}")
        db.execute(f"UPDATE ledger SET {self.cs} = {self.cs} - ? WHERE UserID = ?", amt, ctx.author.id)
        db.commit()

    @set_duel.error
    async def set_duel_error(self, ctx, exc):
        if isinstance(exc, BadArgument):
            await ctx.send("Bad parameters.")

    @Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        pass

def setup(bot):
    bot.add_cog(Duels(bot))
    