#!python3
# coding=UTF-8
import discord
from discord.ext import commands
import aiohttp
import re
from datetime import timedelta
import traceback
import os
import yaml
from random import choice, randint

## load config
with open("config.yml", "r") as configFile:
    try:
        config = yaml.safe_load(configFile)
    except yaml.YAMLError as exc:
        print(exc)
        exit()

owner = config["owner"]
admins = config["admins"]
token = config["token"]

bot = commands.Bot(command_prefix='£', description="MHoC Bot does MHoC things. Why do you want to know?")

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    print(discord.utils.oauth_url(bot.user.id))

async def on_message(message):
    channel = message.channel
    content = message.content
    author = message.author
    if(hasattr(author, 'nick')):
        if(author.nick == None):
            name = author.name
        else:
            name = author.nick
    else:
        name = author.name
    if(author.id == bot.user.id):
        return
#    if(author.id == "158660378040074241"):
#        for word in ["BG", "BEAGLING", "SHE", "BEAGLING GIRL", "THEY", "THEM", "THEIR", "WHATSTHEIRFACE", "AARDVARK", "NIFFALO"]:
#            if("{}".format(word) in content.upper()):
#                await bot.delete_message(message)
#                await bot.send_message(author, "Your message about beagling girl has been deleted. We're disappointed, jas. Message: ```{}```".format(content))
#                print("{}: {}\n".format(name, content))
    if(channel.id != "435842067550437386"):
        return
    if(len(content) > 280):
        print("{}: {} [{}]\n".format(name, content, len(content)))
        await bot.delete_message(message)
        await bot.send_message(author, "Your tweet was longer than 280 characters and has been deleted. Tweet: ```{}```".format(content))

bot.add_listener(on_message)

async def on_message_edit(before, after):
    channel = after.channel
    content = after.content
    author = after.author
    if(author.id == bot.user.id):
        return
    if(channel.id != "435842067550437386"):
        return
    if(len(content) > 280):
        if(author.nick == None):
            name = author.name
        else:
            name = author.nick
        print("{}: {} [{}]".format(name, content, len(content)))
        await bot.delete_message(after)
        await bot.send_message(author, "Your edited tweet was longer than 280 characters and has been deleted. Tweet: ```{}```".format(content))

bot.add_listener(on_message_edit)

@bot.command(pass_context=True, hidden=True)
async def setname(ctx, *, name):
    if ctx.message.author.id not in owner:
        return
    name = name.strip()
    if name != "":
        try:
            await bot.edit_profile(username=name)
        except:
            await bot.say("Failed to change name")
        else:
            await bot.say("Successfuly changed name to {}".format(name))
    else:
        await bot.send_cmd_help(ctx)

@bot.command(pass_context=True, hidden=True)
async def heyman(ctx):
    man = """Hey man, FUCK OFF
you little cunt, its too far
You are the reason for toxicity
there is no reason to vandalise the letter
what's your problem?"""
    await bot.say(man)

@bot.event
async def on_command_error(error, ctx):
    channel = ctx.message.channel
    if isinstance(error, commands.MissingRequiredArgument):
        await send_cmd_help(ctx)
    elif isinstance(error, commands.BadArgument):
        await send_cmd_help(ctx)
    elif isinstance(error, commands.CommandInvokeError):
        print("Exception in command '{}', {}".format(ctx.command.qualified_name, error.original))
        traceback.print_tb(error.original.__traceback__)

@bot.command(pass_context=True, no_pm=True)
async def trumptweet(ctx, *, tweet):
    author = ctx.message.author
    await bot.delete_message(ctx.message)
    if author.id not in owner and  author.id not in admins:
        await bot.send_message(author, "You don't have permission to use the command `£trumptweet`")
        return
    embed=discord.Embed(title="Tweet by realDonaldTrump",description=tweet)
    embed.set_author(name="Twitter",icon_url="https://seeklogo.com/images/T/twitter-2012-negative-logo-5C6C1F1521-seeklogo.com.png")
    embed.set_thumbnail(url="https://pbs.twimg.com/profile_images/874276197357596672/kUuht00m.jpg")
    await bot.say(embed=embed)

@bot.command(pass_context=True, no_pm=True)
async def avatar(ctx, member: discord.Member):
    """Show a user's avatar"""
    await bot.reply("{}".format(member.avatar_url))

@bot.command(pass_context=True, no_pm=True)
async def sicon(ctx):
    """Show the server icon"""
    await bot.reply("{}".format(ctx.message.server.icon_url))

@bot.command(pass_context=True)
async def sid(ctx):
          """Show the server ID"""
          await bot.say("`{}`".format(ctx.message.server.id))

@bot.command(pass_context=True, hidden=True)
async def setavatar(ctx, url):
        if ctx.message.author.id not in owner:
                return
        async with aiohttp.ClientSession() as session:
                async with session.get(url) as r:
                        data = await r.read()
        await bot.edit_profile(avatar=data)
        await bot.say("I changed my icon")

@bot.command(pass_context=True)
async def getinfo(ctx):
    if ctx.message.author.id not in owner:
        return
    print(ctx.message.channel)
    print(ctx.message.channel.id)

@bot.command()
async def servers():
        """Bot server count"""
        await bot.say("**I'm in {} Server!**".format(len(bot.servers)))

@bot.event
async def send_cmd_help(ctx):
    if ctx.invoked_subcommand:
        pages = bot.formatter.format_help_for(ctx, ctx.invoked_subcommand)
        for page in pages:
            em = discord.Embed(description=page.strip("```").replace('<', '[').replace('>', ']'),
                               color=discord.Color.blue())
            await bot.send_message(ctx.message.channel, embed=em)
    else:
        pages = bot.formatter.format_help_for(ctx, ctx.command)
        for page in pages:
            em = discord.Embed(description=page.strip("```").replace('<', '[').replace('>', ']'),
                               color=discord.Color.blue())
            await bot.send_message(ctx.message.channel, embed=em)

@bot.command(pass_context=True)
async def ping():
    """Pong!"""
    await bot.reply("Pong!")

bot.run(token)