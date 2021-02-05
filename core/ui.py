import discord

from discord.ext import commands


class Ui(commands.Cog):
    """
    UI features
    snips - single line, single backtick
    blurbs - single line, triple backtick (formatted)
    blocks - multi line, triple backtick
    embeds - embeds
    """

    # properties / defaults
    blurb_prefixes = {
        'success': 'md\n# Success:',
        'warning': 'fix\n# Warning:',
        'notice': 'css\n#',
        'error': 'cs\n# Error:'
    }


    # cwasses
    class EmbedContent():
        """
        Note : fields is a list of dicts
        [{'name': '\a', 'value': '\a', 'inline': 'False'}]
        """

        def __init__(self, **kwargs):
            self.title = '\a'
            self.colour = 0x2E97F9
            self.thumb = None
            self.desc = ''
            self.fields = None
            self.image = None
            self.footer = None
        
            for key in kwargs:
                setattr(self, key, kwargs[key])



    # constructicons roll out
    def __init__(self, bot):
        self.bot = bot
        self.logs = self.bot.get_cog('Logs')

    

    
    # snips
    async def send_snip(self, ctx, *args):
        return await ctx.send(f'` {" ".join(args)} `')

    async def edit_snip(self, tar, *args):
        await tar.edit(content=f'` {" ".join(args)} `')


    # blurbs
    async def send_blurb(self, ctx, type, *args):
        type = type if type in self.blurb_prefixes else 'notice'
        return await ctx.send(f'```{self.blurb_prefixes[type]} {" ".join(args)}```')

    async def edit_blurb(self, tar, type, *args):
        type = type if type in self.blurb_prefixes else 'notice'
        await tar.edit(content=f'```{self.blurb_prefixes[type]} {" ".join(args)}```')


    # blocks
    async def send_block(self, ctx, style, *args):
        return await ctx.send(f'```{style}\n{" ".join(args)}```')

    async def edit_block(self, tar, style, *args):
        await tar.edit(content=f'```{style}\n{" ".join(args)}```')


    # embeds
    async def send_embed(self, ctx, ec: EmbedContent):

        ebd = discord.Embed(title=ec.title, color=ec.colour, description=ec.desc)

        if ec.thumb is not None:
            ebd.set_thumbnail(url=ec.thumb)

        if ec.image is not None:
            ebd.set_image(url=ec.image)

        if ec.footer is not None:
            ebd.set_footer(text=ec.footer)

        if ec.fields is not None:
            for f in ec.fields:
                ebd.add_field(name=f.get('name'), value=f.get('value'), inline=eval(f.get('inline')))

        return await ctx.send(embed=ebd)


    async def edit_embed(self, tar, *args):
        pass


# attach to bot
def setup(bot):
    bot.add_cog(Ui(bot))