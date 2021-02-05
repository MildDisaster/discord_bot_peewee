import os
import discord

from discord.ext import commands

class Cogs(commands.Cog):
    """
    Cog maintenance 
    """

    # properties / defaults
    cog_path_list = './cogs'
    cog_path_load = 'cogs.'
    

    # constructicons roll out
    def __init__(self, bot):
        self.bot = bot
        self.ui = self.bot.get_cog('Ui')
        self.logs = self.bot.get_cog('Logs')
        self.settings = self.bot.get_cog('Settings')

        # load up any previously loaded cogs
        for cog in self.settings.cogs.value:
            try:
                self.bot.load_extension(self.cog_path_load+cog)
                print(f'Loading cog: {cog} ... ok')
            except Exception as error:
                print(f'Loading cog: {cog} ... failed : {error}')


    # log via decorator
    async def log_use(self, ctx):
        await self.logs.msg(f'{ctx.author.display_name} invoked: \'{ctx.command} {" ".join(ctx.args[2:])}\'')


    # some checks
    def check_user_owner(self, ctx):
        return ctx.author.id == self.settings.owner_id.value

    def check_user_admin(self, ctx):
        usr_roles = set([x.id for x in ctx.author.roles])
        adm_roles = set([role_id for role_id in self.settings.admin_roles.value])
        return usr_roles & adm_roles

    def check_channel_admin(self, ctx):
        return ctx.channel.id == self.settings.chan_admin.value
     
    def check_channel_general(self, ctx):
        return ctx.channel.id == self.settings.chan_general.value


    # commands
    @commands.command(
        brief='List cogs',
        description='Lists all cogs currently loaded, or available.',
        hidden=True
    )
    @commands.before_invoke(log_use)
    async def list_cogs(self, ctx):

        # checks
        if not self.check_user_admin(ctx):
            await self.ui.send_blurb(ctx, 'error', f'command not available to you')
            return

        if not self.check_channel_admin(ctx):
            await self.ui.send_blurb(ctx, 'error', f'command not available here')
            return

        # do the thing
        longest = -1
        for fn in os.listdir(self.cog_path_list):
            if len(fn[:-3]) > longest:
                longest = len(fn[:-3])
        longest += 8

        output = f'\u250F\u2501 Cog listing for {self.settings.fullname.value} \u2501\u257E \n'
        cf = cl = 0
        
        for fn in os.listdir(self.cog_path_list):
            if fn.endswith('.py'):        
                spacing = " " * (longest - len(fn[:-3]))
                if fn[:-3] in self.settings.cogs.value:
                    output += f'\u2523 {fn[:-3]}{spacing}..loaded \n'
                    cl += 1
                else:
                    output += f'\u2523 {fn[:-3]} \n'
            cf += 1

        output += f'\u2517\u2501\u2501 Total:{cf} \u2501 Loaded:{cl} \u2501\u257E'

        await self.ui.send_block(ctx, 'css', output)

    
    @commands.command(
        brief='Loads a cogs',
        description='Loads a cog into existence. The cog will be reloaded during bot restarts.',
        hidden=True
    )
    @commands.before_invoke(log_use)
    async def load_cog(self, ctx, cog):
        
        # checks
        if not self.check_user_admin(ctx):
            await self.ui.send_blurb(ctx, 'error', f'command not available to you')
            return

        if not self.check_channel_admin(ctx):
            await self.ui.send_blurb(ctx, 'error', f'command not available here')
            return

        # do the thing
        try:
            self.bot.load_extension(self.cog_path_load+cog)

        except Exception as error:
            await self.ui.send_blurb(ctx, 'error', f'cog {cog} failed to load: {type(error)}-{error}')

        else:
            self.settings.cogs.value.append(cog)
            self.settings.cogs.save()
            await self.ui.send_blurb(ctx, 'success', f'cog {cog} loaded')


    @commands.command(
        brief='Unloads a cog',
        description='Stops and unloads a cog. The cog will no longer be loaded upon bot restarts.',
        hidden=True
    )
    @commands.before_invoke(log_use)       
    async def unload_cog(self, ctx, cog):
        
        # checks
        if not self.check_user_admin(ctx):
            await self.ui.send_blurb(ctx, 'error', f'command not available to you')
            return

        if not self.check_channel_admin(ctx):
            await self.ui.send_blurb(ctx, 'error', f'command not available here')
            return

        # do the thing
        try:
            self.bot.unload_extension(self.cog_path_load+cog)
        
        except Exception as error:
            await self.ui.send_blurb(ctx, 'error', f'cog {cog} failed to unload: {type(error)}-{error}')

        else:
            self.settings.cogs.value.remove(cog)
            self.settings.cogs.save()
            await self.ui.send_blurb(ctx, 'success', f'cog {cog} unloaded')


    @commands.command(
        brief='Reloads a cog',
        description='Attempts to unload and then load a cog. If the cog reloads successfully, it will be loaded upon bot restarts.',
        hidden=True
    )
    @commands.before_invoke(log_use)
    async def reload_cog(self, ctx, cog):       
        
        # checks
        if not self.check_user_admin(ctx):
            await self.ui.send_blurb(ctx, 'error', f'command not available to you')
            return

        if not self.check_channel_admin(ctx):
            await self.ui.send_blurb(ctx, 'error', f'command not available here')
            return

        # do the thing
        try:
            self.bot.unload_extension(self.cog_path_load+cog)

        except Exception as error:
            status = await self.ui.send_blurb(ctx, 'error', f'cog {cog} failed to unload: {type(error)}-{error}')
        
        else:
            status = await self.ui.send_blurb(ctx, 'success', f'cog {cog} unloaded, attempting to reload')

            try:
                self.bot.load_extension(self.cog_path_load+cog)
            
            except Exception as error:
                self.settings.cogs.value.remove(cog)
                self.settings.cogs.save()
                await self.ui.edit_blurb(status, 'error', f'cog {cog} failed to reload: {type(error)}-{error}')

            else:
                await self.ui.edit_blurb(status, 'success', f'cog {cog} reloaded')
                   


    # # listeners
    # @commands.Cog.listener()
    # async def on_ready(self):
    #     pass


# attach to bot
def setup(bot):
    bot.add_cog(Cogs(bot))
