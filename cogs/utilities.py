import discord
from discord import SlashCommandGroup
from discord.ext import commands


class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    group = SlashCommandGroup(name="utility", description="Utility commands")

    @group.command(name="ping", description="Ping the bot.")
    async def ping(self, ctx: discord.ApplicationContext):
        await ctx.respond('Pong.')


def setup(bot):
    bot.add_cog(Utilities(bot))
