from apscheduler.triggers.cron import CronTrigger
from discord import Activity, ActivityType
from discord.ext.commands import Cog
from discord.ext.commands import command

class Meta(Cog):
    def __init__(self, bot):
        self.bot = bot

        self._message = "playing $help"

        bot.scheduler.add_job(self.set, CronTrigger(second=0))

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        self._message = value
    
    async def set(self):
        await self.bot.change_presence(activity=Activity(name="$help", type=getattr(ActivityType, "playing", ActivityType.playing)))

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("meta")


def setup(bot):
    bot.add_cog(Meta(bot))
    