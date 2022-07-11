import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Setup intent
intents = discord.Intents.default()
intents.message_content = True

# Create bot
bot = commands.Bot(command_prefix='$', case_insensitive=True, intents=intents)

# Load cogs
cog_names = [
    'utilities',
    'roles'
]
for cog in cog_names:
    bot.load_extension(f'cogs.{cog}')


def is_bot(m):
    return m.author == bot.user


@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))
    channel = bot.get_channel(int(os.getenv('ROLE_BTNS_CHNL_ID')))
    # await channel.purge(check=is_bot)
    # await button(channel)

## Button Command

@bot.command()
@commands.has_permissions(manage_messages=True)
async def button(c):
    if isinstance(c, commands.Context):
        await c.message.delete()
    embed = discord.Embed(title="Change your party role",
                          description="You can now change your party role without Moderator help. Please do not abuse it! For a full list of parties, click the grey button below. If your party cannot be found, please contact a Moderator.",
                          color=0x2b823d)
    embed.set_footer(text="MHoC Bot")
    embed.set_image(url="https://cdn.discordapp.com/attachments/994920937797468252/994937142453227540/unknown.png")
    view = Buttons()
    view.add_item(discord.ui.Button(label="List of parties", style=discord.ButtonStyle.link,
                                    url="https://docs.google.com/spreadsheets/d/1KJR4fJp9LpyR8bKrSjhOa3uvuyUutldHs8IGiIpD5u8/edit#gid=1351102681"))
    await c.send(embed=embed, view=view)


class Buttons(discord.ui.View):
    def __init__(self, *, timeout=None):
        super().__init__(timeout=timeout)
        print(super().is_persistent())

    @discord.ui.button(custom_id="select-role-button", label="Change your party role",
                       style=discord.ButtonStyle.primary, emoji="😃")
    async def change_role_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        roles = await get_roles(g=interaction.guild)
        embed = discord.Embed(title="Change your party role",
                              description="Select the correct party role with the dropdown below.", color=0x2b823d)
        await interaction.response.send_message(embed=embed, view=SelectView(roles=roles), ephemeral=True)


@button.error
async def button_error(ctx, error):
    desc = ""
    if isinstance(error, commands.MissingPermissions):
        desc = "Don't touch things you don't know how to use."
    if isinstance(error, Exception):
        desc = error
    embed = discord.Embed(title="Oh dear!", description=desc, color=0xcd2323)
    await ctx.send(embed=embed)


## Party select dropdown + associated view

class PartySelect(discord.ui.Select):
    def __init__(self, roles=[]):
        options = [discord.SelectOption(label=r.name) for r in roles]
        super().__init__(placeholder="Select a role", max_values=1, min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        roles = await get_roles(g=interaction.guild)
        try:
            await interaction.user.remove_roles(*roles)
            for r in roles:
                if self.values[0] == r.name:
                    await interaction.user.add_roles(r)
                    await interaction.response.edit_message(content=f"You have joined **{self.values[0]}**", view=None,
                                                            embed=None)
                    await bot.get_channel(int(os.getenv('ROLE_LOG_CHNL_ID'))).send(
                        f"**{interaction.user.mention}** has joined **{self.values[0]}**")
        except Exception as e:
            embed = discord.Embed(title="Oh dear!", description=e, color=0xcd2323)
            await interaction.response.edit_message(embed=embed, view=None)


class SelectView(discord.ui.View):
    def __init__(self, *, timeout=30, roles=[]):
        super().__init__(timeout=timeout)
        self.add_item(PartySelect(roles=roles))

    async def on_timeout(self):
        print("view timed out")
        print(type(self))
        self.clear_items()


## JWBot Mute Wrapper

@bot.command()
@commands.has_permissions(manage_messages=True)
async def mute(ctx, user: discord.Member, time, *reason):
    if len(reason) == 0:
        raise Exception("You must give a reason to mute someone.")
    await ctx.send("<@412754716884336650> Mute {0.mention} {1} {2}".format(user, time, " ".join(reason)))


@mute.error
async def mute_error(ctx, error):
    desc = ""
    if isinstance(error, commands.MissingPermissions):
        desc = "Don't touch things you don't know how to use."
    if isinstance(error, Exception):
        desc = error
    embed = discord.Embed(title="Oh dear!", description=desc, color=0xcd2323)
    await ctx.send(embed=embed)


# Run bot instsance
bot.run(os.getenv('TOKEN'))
