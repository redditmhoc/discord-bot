import discord
from discord import SlashCommandGroup
from discord.ext import commands
from party_role_select import create_prompt


async def get_dynamic_positional_role(guild=discord.Guild, start=True):
    if start:
        name = "=Start dynamic party roles="
    else:
        name = "=End dynamic party roles="
    return discord.utils.get(guild.roles, name=name)


async def get_dynamic_party_roles(guild=discord.Guild):
    roles = []
    start_role, end_role = await get_dynamic_positional_role(guild, True), await get_dynamic_positional_role(guild,
                                                                                                             False)
    for r in guild.roles:
        greater, lesser = False, False
        if r > end_role:
            greater = True
        if r < start_role:
            lesser = True
        if greater and lesser:
            roles.append(r)
    return roles


class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    group = SlashCommandGroup(name="roles", description="Role commands")

    @group.command(name="listpartyroles", description="List available party roles.")
    @discord.default_permissions(
        manage_roles=True
    )
    async def list_party_roles(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        roles = await get_dynamic_party_roles(ctx.guild)
        response = f"**Party roles found in {ctx.guild.name}:**\n"
        for role in roles:
            response += f"{role.name} ({role.id})\n"
        await ctx.send_response(response)

    @group.command(name="createform", description="Create the party role select form manually.")
    @discord.default_permissions(manage_guild=True)
    async def create_form(self, ctx: discord.ApplicationContext):
        await create_prompt(ctx.channel)
        await ctx.send_response("Created", ephemeral=True)


def setup(bot):
    bot.add_cog(Roles(bot))
