import discord
import aiohttp
import urllib.parse

from discord.ext import commands

class UrbanDictionary(commands.Cog):
    """
    Lookup using unofficial urbandictionary api
    """

    # properties / defaults
    defaults = {
        'ud_channels': ['ALL'],
        'ud_api_url': 'http://api.urbandictionary.com/v0/define?term='
    }


    # constructicons roll out
    def __init__(self, bot):
        self.bot = bot
        self.ui = self.bot.get_cog('Ui')
        self.logs = self.bot.get_cog('Logs')
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


    # log via decorator
    async def log_use(self, ctx):
        await self.logs.msg(f'{ctx.author.display_name} invoked: \'{ctx.command} {" ".join(ctx.args[2:])}\'')


    # some checks
    def check_channel_allowed(self, ctx):
        ac = self.settings.ud_channels.value
        return ctx.channel.id in ac or 'ALL' in ac


    # commands
    @commands.command(
        brief='UrbanDictionary lookup',
        description='Query urbandictionary.com for first matching result.'
    )
    @commands.before_invoke(log_use)
    async def ud(self, ctx, *args):
        
        # checks
        if not self.check_channel_allowed(ctx):
            await self.ui.send_blurb(ctx, 'error', f'command not available here')
            return  

        # do the thing
        query_url = f'{self.settings.ud_api_url.value}{urllib.parse.quote(" ".join(args))}'

        async with aiohttp.ClientSession() as session:
            async with session.get(query_url) as get:
                if get.status == 200:
                    response = await get.json()

                    ebc = self.ui.EmbedContent(
                        title='**UrbanDictionary** says :',
                        fields=[
                            {
                                'name': f' \n\u22A2** {" ".join(args)} **', 
                                'value': f'\n{response["list"][0]["definition"]}\n \n',
                                'inline': 'False'
                            },
                            {
                                'name': f'\u22A2** Example **', 
                                'value': f'\n{response["list"][0]["example"]}', 
                                'inline': 'False'
                            },
                            {
                                'name': '\a', 
                                'value': f'\u22A2** Author **: {response["list"][0]["author"]}\n'
                                         f'\u22A2** link **: [{response["list"][0]["permalink"]}]({response["list"][0]["permalink"]})',
                                'inline': 'False'
                            }
                        ]
                    )
       
                    await self.ui.send_embed(ctx, ebc)
                
                else:
                    await self.ui.send_blurb(ctx, 'error', f'Error: {get.status}')



# attach to bot
def setup(bot):
    bot.add_cog(UrbanDictionary(bot))