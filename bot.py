import discord
 
from discord.ext import commands
from discord.ext.commands import CommandNotFound, MissingRequiredArgument


# prep some things
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='?', intents=intents, description='')


# make magic happen
if __name__ == '__main__':

    """
    Another attempt to make a somewhat modular discord bot using discord.py
    Some assumptions : 
        - single server client; this is a stay at home cozy kind of bot
        - not using dicsord.py checks, it gets finicky to make custom checks in cogs
        - not using the baked in exception handling to send status feedback.  I'm
          pulling blanks on how to make it anything but boring/sterile (because I R dumb).  
          Might change my mind on this later (not the dumb bit)
    """

    # disable built in help
    bot.remove_command('help')
    
    # core cogs (ordered)
    core = ['ui', 'settings', 'logs', 'cogs', 'help']

    # load core cogs
    for c in core:
        filename = f'core.{c}'
        try:
            bot.load_extension(filename)
            print(f'Loading cog: {filename} ... ok')
        except Exception as err:
            print(f'Loading cog: {filename} ... failed')
            print(f'Error: {type(err)} : {err}')

    # pull some vals for happy boot
    logs = bot.get_cog('Logs')
    settings = bot.get_cog('Settings')
    
    bot.command_prefix = settings.get_prefix
    bot.description = settings.desc.value


# events
@bot.event
async def on_connect():
    print(f'\n\nBooting up {bot.user.name}')
    print(f' - discord.py version {discord.__version__}\n')


@bot.event
async def on_ready():
    print(f'\n\nLogged in as {bot.user.name} - {bot.user.id}')

    try:
        await bot.change_presence(activity=discord.Activity(
                type=settings.presence_type.value,
                name=f' {settings.presence_text.value}'
            ))
        
    except Exception as error:
        await logs.msg(f'unable to set presence: {error}')

    else:
        await logs.msg(f'presence set')


# bombs away
bot.run(settings.app_token.value, bot=True, reconnect=True)
