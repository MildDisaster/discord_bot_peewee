import discord

from discord.ext import commands
from textwrap import wrap


class Help(commands.Cog):
    """
    Custom help command
    Some differences :
        - if hidden property is true, item will be shown in admin channel
    """

    # properties / defaults


    # constructicons roll out
    def __init__(self, bot):
        self.bot = bot
        self.ui = self.bot.get_cog('Ui')
        self.logs = self.bot.get_cog('Logs')
        self.settings = self.bot.get_cog('Settings')

    
    # log via decorator
    async def log_use(self, ctx):
        await self.logs.msg(f'{ctx.author.display_name} invoked: \'{ctx.command} {" ".join(ctx.args[2:])}\'')


    # some checks
    def check_channel_admin(self, ctx):
        return ctx.channel.id == self.settings.chan_admin.value
     
    def check_channel_general(self, ctx):
        return ctx.channel.id == self.settings.chan_general.value


    
    # commands
    @commands.command(
        brief='This dialogue ><',
        description='Needing help with help is far too meta for me this evening.'
    )
    @commands.before_invoke(log_use)
    async def help(self, ctx, *args):

        if not bool(args):
            # prep
            longest = -1        
            sorted_list = sorted(self.bot.commands, key=lambda x: x.cog.qualified_name)

            for c in sorted_list:
                if len(c.name) > longest:
                    longest = len(c.name)

            # cook
            longest += 8
            last_cog = ''
            output = f'\u250F\u2501 Help menu for {self.settings.fullname.value} \u2501\u257E \n'
            
            for c in sorted_list:
                
                # if command is hidden, check context is from admin channel
                if not self.check_channel_admin(ctx) and c.hidden:
                    pass

                else:
                    if c.cog.qualified_name is not last_cog:
                        output += f'\u2523 {c.cog.qualified_name}: \n'
                        last_cog = c.cog.qualified_name

                    spacing = " " * (longest - len(c.name))
                    output += f'\u2503   {c.name}{spacing}{c.brief} \n'

            output += f'\u2517\u2501\u2501 Type \'{self.settings.prefix.value[0]}help [command]\' for more info on a command \u2501\u257E'

            await self.ui.send_block(ctx, 'css', output)
            return

        else:          
            cmd = self.bot.get_command(args[0])

            # check if command doesn't exist
            if cmd == None:
                await self.ui.send_blurb(ctx, 'error', f'command not found in help menu')
                return

            # if command is hidden, check context is from admin channel
            if not self.check_channel_admin(ctx) and cmd.hidden:
                await self.ui.send_blurb(ctx, 'error', f'help is unavailable for that command in this channel')
                return

            # output detailed help dialog
            paragraph = wrap(cmd.description, width=60, initial_indent=' ')

            output =  f'\u250F\u2501 Detailed help menu for {self.settings.fullname.value} \u2501\u257E \n' \
                      f'\u2503 \n' \
                      f'\u2523 Command: {cmd.name}\n'

            for line in paragraph:
                output += f'\u2503   {line}\n'

            output += f'\u2503 \n' \
                      f'\u2523 Usage: {self.settings.prefix.value[0]}{cmd.name} {cmd.signature}\n' \
                      f'\u2517\u2501\u2501\u2501\u257E' 

            await self.ui.send_block(ctx, 'css', output)
            return



# attach to bot
def setup(bot):
    bot.add_cog(Help(bot))