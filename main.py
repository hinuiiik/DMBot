import random
import discord
import sys
import os
from discord.ext import commands
from discord.utils import get
from discord import SyncWebhook
import json

admins = [00000000000000] # User IDs of Admins
guild_id = 0000000000000000 # Discord Server ID
category_id = "DMs" # Discord Channel Category Name

# global replies

# if not os.path.isfile("replies.json"):
#     with open("replies.json", "w+") as g:
#         json.dump({}, g, indent=1)
#     g.close()

if not os.path.isfile("dm_ids.json"):
    with open("dm_ids.json", "w+") as g:
        json.dump({'': {'webhook_url': '', 'channel_id': ''}}, g, indent=1)
    g.close()


# def file_update():
#     global replies
#     with open("replies.json", "r") as g:
#         replies = json.load(g)
# 
#         # json.dump(ids, f, indent=1)
#     g.close()


def attachment_list(message):
    dm_attach = message.content
    for x in message.attachments:
        dm_attach = dm_attach + " " + x.url
    return dm_attach


# file_update()

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix='.', description="test", intents=intents)

with open("dm_ids.json", "r") as f:
    ids = json.load(f)
f.close()


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    global ids
    guild = client.get_guild(guild_id) 
    channelcategory = get(guild.channels, name=category_id) 
    if message.author == client.user or message.author.bot:
        return

    for userid in ids:
        if str(message.channel.id) == ids[userid]["channel_id"]:
            user = await client.fetch_user(userid)
            await user.send(attachment_list(message))

    if isinstance(message.channel, discord.DMChannel):
        try: # If user has already messaged the bot once
            SyncWebhook.from_url(ids[str(message.author.id)]["webhook_url"]).send(attachment_list(message),
                                                                                  username=message.author.name,
                                                                                  avatar_url=message.author.avatar)
        except KeyError: # If user has not messaged the bot at least once
            user = await client.fetch_user(message.author.id)
            await user.send("Warning: All messages sent to this bot are logged and readable by this bot's owners. By "
                            "continuing, you accept this. Your first message has not been logged. Your subsequent "
                            "messages will be logged.")
            dm_channel = await guild.create_text_channel(str(message.author).replace("#", "-"), overwrites={},
                                                         category=channelcategory)
            webhook = await dm_channel.create_webhook(name="user")
            # SyncWebhook.from_url(webhook.url).send(attachment_list(message),
            #                                        username=message.author.name, avatar_url=message.author.avatar)
            ids[str(message.author.id)] = {"webhook_url": str(webhook.url), "channel_id": str(dm_channel.id)}
            with open("dm_ids.json", "w") as f:
                json.dump(ids, f, indent=1)
                # ids = json.load(f)
            f.close()

    # if not message.content.startswith("."):
    #     for i in replies:
    #         if i in message.content.strip().lower():
    #             await message.reply(replies[i])
    #             return

    await client.process_commands(message)



# @client.command()
# async def upload(ctx):
#     if ctx.author.id in admins:
#         await ctx.reply(file=discord.File(r'replies.json'))


# @client.command()
# async def update(ctx):
#     if ctx.author.id in admins:
#         file_update()
#         await ctx.reply("updated!")


# @client.command()
# async def add(ctx, args, args2: str = None):
#     if ctx.author.id in admins:
#         global replies
#         if args in replies:
#             await ctx.reply(args + " is already added")
#         else:
#             if args2 is None:
#                 replies[args] = args
#             else:
#                 replies[args] = args2
#             with open("replies.json", "w") as g:
#                 json.dump(replies, g, indent=1)
#             g.close()
# 
#             await ctx.reply("added " + args)
#             file_update()


# @client.command()
# async def remove(ctx, args):
#     if ctx.author.id in admins:
#         try:
#             del replies[args]
#             with open("replies.json", "w") as g:
#                 json.dump(replies, g, indent=1)
#             g.close()
#             await ctx.reply(f"{args} has been removed")
#             file_update()
#         except KeyError:
#             await ctx.reply("command borke :( key no existo")


@client.group(pass_context=True)
async def send(ctx):
    if ctx.author.id in admins:
        if ctx.invoked_subcommand is None:
            await ctx.send('Parameters: `.send (channel/dm) ID "message contents"`')


@send.group(pass_context=True)
async def channel(ctx, uid: int, message):
    if ctx.author.id in admins:
        channelsend = await ctx.bot.fetch_channel(uid)
        await channelsend.send(message)


@channel.error
async def test_error(ctx):
    await ctx.send('Parameters: `.send channel ID "message contents"`')


@send.group(pass_context=True)
async def dm(ctx, uid: int, message):
    if ctx.author.id in admins:
        dmuser = await ctx.bot.fetch_user(uid)
        await dmuser.send(message)


@dm.error
async def test_error(ctx):
    await ctx.send('Parameters: `.send dm ID "message contents"`')


@client.command()
async def react(ctx):  # msg: discord.Message
    if ctx.author.id in admins:
        await ctx.message.add_reaction(":thumbs_up:")


# @react.error
# async def test_error(ctx):
#     await ctx.send('''Parameters: `.react Channel_ID "emoji"`
#                    Emoji example: `<:>`''')

client.run(sys.argv[1])
