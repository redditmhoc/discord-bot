import discord
from discord.ext import commands
from dotenv import load_dotenv

TOKEN = ''
load_dotenv(override=True)


START = 994992781535744121
END   = 994992814637199380

BTN_CHANNEL = 995018477704327248
LOG_CHANNEL = 995023454451536082

PARTY_EMOJI = {"Labour": " <:labour:313396345119571968>","Coalition!": " <:Coalition:986324142854918195>"}

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', case_insensitive=True, intents=intents)

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))
    channel = bot.get_channel(BTN_CHANNEL)
    await channel.purge(check=is_bot)
    await button(channel)


## Utilities

def is_bot(m):
    return m.author == bot.user

async def get_roles(g = discord.guild):
    roles = []
    for r in g.roles:
        greater, lesser = False, False
        if r > g.get_role(START):
            greater = True
        if r < g.get_role(END):
            lesser = True
        if greater and lesser:
            roles.append(r)
    return roles

@bot.command()
async def partyroles(ctx):
    roles = await get_roles(ctx.guild)
    for r in roles:
        await ctx.send(f"Found party role {r.name} ({r.id}).")

## Button Command

@bot.command()
@commands.has_permissions(manage_messages=True)
async def button(c):
    if isinstance(c, commands.Context):
        await c.message.delete()
    embed=discord.Embed(title="Change your party role", description="You can now change your party role without Moderator help. Please do not abuse it! For a full list of parties, click the grey button below. If your party cannot be found, please contact a Moderator.", color=0x2b823d)
    embed.set_footer(text="MHoC Bot")
    embed.set_image(url="https://cdn.discordapp.com/attachments/994920937797468252/994937142453227540/unknown.png")
    view=Buttons()
    view.add_item(discord.ui.Button(label="List of parties",style=discord.ButtonStyle.link,url="https://docs.google.com/spreadsheets/d/1KJR4fJp9LpyR8bKrSjhOa3uvuyUutldHs8IGiIpD5u8/edit#gid=1351102681"))
    await c.send(embed=embed,view=view)

class Buttons(discord.ui.View):
    def __init__(self, *,timeout=None):
        super().__init__(timeout=timeout)
        print(super().is_persistent())
    @discord.ui.button(custom_id="select-role-button",label="Change your party role",style=discord.ButtonStyle.primary,emoji="😃")
    async def change_role_button(self,interaction:discord.Interaction,button:discord.ui.Button):
        roles = []
        g = interaction.guild
        for r in g.roles:
            greater, lesser = False, False
            if r > g.get_role(START):
                greater = True
            if r < g.get_role(END):
                lesser = True
            if greater and lesser:
                roles.append(r)
        embed=discord.Embed(title="Change your party role", description="Select the correct party role with the dropdown below.", color=0x2b823d)
        await interaction.response.send_message(embed=embed, view=SelectView(roles=roles),ephemeral=True)

@button.error
async def button_error(ctx, error):
    desc = ""
    if isinstance(error, commands.MissingPermissions):
        desc = "Don't touch things you don't know how to use."
    if isinstance(error, Exception):
        desc = error
    embed=discord.Embed(title="Oh dear!", description=desc, color=0xcd2323)
    await ctx.send(embed=embed)

## Party select dropdown + associated view

class PartySelect(discord.ui.Select):
    def __init__(self, roles = []):
        options = [discord.SelectOption(label=r.name) for r in roles]
        super().__init__(placeholder="Select a role",max_values=1,min_values=1,options=options)
    async def callback(self, interaction:discord.Interaction):
        roles = await get_roles(g=interaction.guild)
        try:
            await interaction.user.remove_roles(*roles)
            for r in roles:
                if self.values[0] == r.name:
                    if self.values[0] in PARTY_EMOJI:
                        emoji = PARTY_EMOJI[self.values[0]]
                    else:
                        emoji = ""
                    await interaction.user.add_roles(r)
                    await interaction.response.edit_message(content=f"You have joined **{self.values[0]}**", view=None,embed=None)
                    await bot.get_channel(LOG_CHANNEL).send(f"**{interaction.user.mention}** has joined{emoji} **{self.values[0]}**")
        except Exception as e:
            embed=discord.Embed(title="Oh dear!", description=e, color=0xcd2323)
            await interaction.response.edit_message(embed=embed, view=None)


class SelectView(discord.ui.View):
    def __init__(self, *, timeout = 3, roles = []):
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
    embed=discord.Embed(title="Oh dear!", description=desc, color=0xcd2323)
    await ctx.send(embed=embed)

## run the fucking thing

bot.run(TOKEN)
