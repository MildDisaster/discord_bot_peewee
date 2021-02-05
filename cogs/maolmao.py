import discord
import aiohttp
import io

from discord.ext import commands

class Maolmao(commands.Cog):
    """
    The ubiquitous chairman lmao cog
    """

    # properties / defaults
    defaults = {
        'maolmao_keywords': ['lmao', 'smh', 'fml'],
        'maolmao_channels': ['ALL'],
        'maolmao_image': 'https://whatever.your.location.might.be/maolmao.png'
    }


    # constructicons roll out
    def __init__(self, bot):
        self.bot = bot
        self.settings = self.bot.get_cog('Settings')

        # add our configuration
        for item in self.defaults:
            if not hasattr(self.settings, item):
                self.settings.create(item, self.defaults[item])


    # destructicons attack
    def cog_unload(self):
        for item in self.defaults:
            if hasattr(self.settings, item):
                self.settings.delete(item)


    # listeners
    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.id != self.bot.user.id:
            if str(msg.channel.type) == 'text':
                
                ac = self.settings.maolmao_channels.value
                if msg.channel.id in ac or 'ALL' in ac:

                    kw = self.settings.maolmao_keywords.value
                    if msg.content.lower().startswith(tuple(kw)):

                        file_url = self.settings.maolmao_image.value
                        async with aiohttp.ClientSession() as session:
                            async with session.get(file_url) as get:
                                if get.status != 200:
                                    await msg.channel.send(f'{msg.author.mention} LMAO')
                                
                                else:
                                    image = io.BytesIO(await get.read())
                                    await msg.channel.send(file=discord.File(image, file_url))



# attach to bot
def setup(bot):
    bot.add_cog(Maolmao(bot))