import datetime
import sqlite3
import discord
import json

from discord.ext import commands
from peewee import *
from playhouse.sqlite_ext import *


class Settings(commands.Cog):
    """
    Bot configuration 
    """

    # properties / defaults

    # cwasses
    class Setting(Model):
        key = CharField(unique=True)
        value = JSONField()
        modified = DateTimeField(default=datetime.datetime.now)

        class Meta:
            database = SqliteExtDatabase('var/settings.db')


    # constructicons roll out
    def __init__(self, bot):
        self.bot = bot
        self.ui = self.bot.get_cog('Ui')
        self.logs = self.bot.get_cog('Logs') # at this point will return None, check on_connect listener

        # we want to snag all key/value pairs as object properties
        settings = self.Setting.select()
        for s in settings:
            self.__dict__[s.key] = s
            # print(f's: {type(s.value)}: {s.key}: {s.value}')


    # log via decorator
    async def log_use(self, ctx):
        await self.logs.msg(f'{ctx.author.display_name} invoked: \'{ctx.command} {" ".join(ctx.args[2:])}\'')


    # some checks
    def check_user_owner(self, ctx):
        return ctx.author.id == getattr(self, 'owner_id').value

    def check_user_admin(self, ctx):
        usr_roles = set([x.id for x in ctx.author.roles])
        adm_roles = set([role_id for role_id in getattr(self, 'admin_roles').value])
        return usr_roles & adm_roles

    def check_channel_admin(self, ctx):
        return ctx.channel.id == getattr(self, 'chan_admin').value
     
    def check_channel_general(self, ctx):
        return ctx.channel.id == getattr(self, 'chan_general').value



    # return appropriate command prefix based on context
    def get_prefix(self, obj, msg):
        if isinstance(msg.channel, discord.TextChannel):
            return getattr(self, 'prefix').value
        
        elif isinstance(msg.channel, discord.DMChannel):
            return ''

    # settings maintenance (used by cogs during un/loading)
    def create(self, key, value):
        try:
            result = self.Setting.create(key=key, value=value, modified=datetime.datetime.now())
        except IntegrityError:
            pass
        else:
            self.__dict__[key] = result
        

    def delete(self, key):
        try:
            result = self.Setting.get(self.Setting.key == key)
        except DoesNotExist:
            pass
        else:
            result.delete_instance()
            del(self.__dict__[key])


    # commands
    @commands.command(
        brief='List settings',
        description='Lists the current configuration settings.',
        hidden=True
    )
    @commands.before_invoke(log_use)
    async def list_settings(self, ctx):
        
        # checks
        if not self.check_user_admin(ctx):
            await self.ui.send_blurb(ctx, 'error', f'command not available to you')
            return

        if not self.check_channel_admin(ctx):
            await self.ui.send_blurb(ctx, 'error', f'command not available here')
            return

        # do the thing
        longest = -1
        for s in self.Setting.select():
            if len(s.key) > longest:
                longest = len(s.key)
        longest += 8

        output = f'\u250F\u2501 Configuration for {getattr(self, "fullname").value} \u2501\u257E \n'
        for s in self.Setting.select():
            if s.key != 'app_token':
                spacing = " " * (longest - len(s.key))
                output += f'\u2523 {s.key}:{spacing}{s.value}\n'
        
        output += f'\u2517\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u257E'
        await self.ui.send_block(ctx, 'css', output)


    @commands.command(
        brief='Update setting',
        description='Adjust a value for a particular setting.',
        hidden=True
    )
    @commands.before_invoke(log_use)
    async def update_setting(self, ctx, key, *args): ## cast the incoming values into the same type as the target

        # checks
        if not self.check_user_admin(ctx):
            await self.ui.send_blurb(ctx, 'error', f'command not available to you')

        if not self.check_channel_admin(ctx):
            await self.ui.send_blurb(ctx, 'error', f'command not available here')
        
        # do the thing
        try:
            check = self.Setting.get(self.Setting.key == key)
        
        except DoesNotExist:
            await self.ui.send_blurb(ctx, 'error', f'key \'{key}\' does not exist')

        else:
            if type(check.value) is str:
                getattr(self, key).value = str(" ".join(args))

            elif type(check.value) is int:
                getattr(self, key).value = int("".join(args))

            elif type(check.value) is list:
                getattr(self, key).value = list(args)
            
            else:
                await self.ui.send_blurb(ctx, 'error', f'value of {key} is an unknown type')
                return

        getattr(self, key).save()
        await self.ui.send_blurb(ctx, 'success', f'key \'{key}\' has been updated')
                

    @commands.command(
        brief='Refreshes presence',
        description='Loads in new presence values.',
        hidden=True
    )
    @commands.before_invoke(log_use)
    async def refresh_presence(self, ctx):

        # checks
        if not self.check_user_admin(ctx):
            await self.ui.send_blurb(ctx, 'error', f'command not available to you')

        if not self.check_channel_admin(ctx):
            await self.ui.send_blurb(ctx, 'error', f'command not available here')

        # do the thing
        try:
            await self.bot.change_presence(activity=discord.Activity(
                type=getattr(self, 'presence_type').value,
                name=f' {getattr(self, "presence_text").value}'
            ))
        
        except Exception as error:
            await self.ui.send_blurb(ctx, 'error', f'unable to refresh presence: {error}')

        else:
            await self.ui.send_blurb(ctx, 'success', f'presence refreshed, changes may take a moment')



    # listeners
    @commands.Cog.listener()
    async def on_connect(self):
        # kinda need to bootstrap a cyclic dependancy
        # ugly solution, not sure of better one
        self.logs = self.bot.get_cog('Logs')


# attach to bot
def setup(bot):
    bot.add_cog(Settings(bot))
