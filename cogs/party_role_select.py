import discord
from discord.ext import commands
from roles import get_dynamic_party_roles


class PartyRoleSelectButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        custom_id="party_role_select_button",
        label="Change your party role",
        style=discord.ButtonStyle.primary
    )
    async def party_role_select_button(self, button=discord.ui.Button, interaction=discord.Interaction):
        roles = get_dynamic_party_roles(guild=interaction.guild)
        await interaction.response.send_message("test")


async def create_prompt(channel=discord.TextChannel):
    info_embed = discord.Embed(
        title="Change your party role",
        description='''
        You can now change your party role without Moderator help. Please do not abuse it! For a full list of parties, click the grey button below. If your party cannot be found, please contact a Moderator.
        ''',
        color=0x2b823d
    )
    info_embed.set_image(url="https://cdn.discordapp.com/attachments/994920937797468252/994937142453227540/unknown.png")
    await channel.send(embed=info_embed, view=PartyRoleSelectButtons)