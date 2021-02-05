import logging
import discord
import datetime

from logging.handlers import RotatingFileHandler
from discord.ext import commands

class Logs(commands.Cog):
    """
    Logging for our bot
    There is a bit of a chicken vs egg with the settings cog.
    Also the log channel is only accessible sometime after on_ready.
    As this cog is loaded well before any connection to discord server is made.
    So things are a bit clunky.
    """

    # properties / defaults
    lf = logging.Formatter('%(asctime)s %(message)s', '%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger('Logger')


    # constructicons roll out
    def __init__(self, bot):
        self.bot = bot
        self.settings = self.bot.get_cog('Settings')

        self.log_channel = None # set via on_ready
        
        lh = RotatingFileHandler(
            filename=self.settings.log_file.value,
            maxBytes=self.settings.log_file_size.value * 1024,
            backupCount=2
        )
        lh.setFormatter(self.lf)

        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(lh)



    # log method
    async def msg(self, msg):
        # send to file
        self.logger.info(msg)

        # send to channel
        try:
            await self.log_channel.send(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - {msg}')
        except AttributeError:
            pass



    # listeners
    @commands.Cog.listener()
    async def on_ready(self):
        
        server = self.bot.get_guild(self.settings.server_id.value)
        self.log_channel = discord.utils.get(server.text_channels, id=self.settings.chan_logs.value)

        await self.msg('Logging initialized')


# attach to bot
def setup(bot):
    bot.add_cog(Logs(bot))