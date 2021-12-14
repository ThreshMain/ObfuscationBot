import asyncio
import os
from config import Config
import discord
from discord.ext import commands
from discord.utils import escape_mentions
from interactions.InitExchangeButton import InitExchange
import logging

VERSION = "1.0-ALPHA.4.1"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('DiscordBot')

config: Config = Config(logger)
token: str = os.getenv("TOKEN")

bot = commands.Bot(command_prefix="!", owner_id=470490558713036801, intents=discord.Intents.all())
guild: discord.Guild


def create_welcome_embed() -> discord.Embed:
    welcome_embed: discord.Embed = discord.Embed(colour=discord.Color.orange())
    welcome_embed.title = "Obfuscation bot"
    welcome_embed.url = config.sourceLink
    welcome_embed.description = "Ahoj, tenhle bot anonymně přepošle zprávu do cílového kanálu tvé volby.\n\
    Zprávy mohou obsahovat přílohy."
    welcome_embed.set_footer(text=VERSION)
    welcome_embed.add_field(
        name="Návod na použití",
        value="Come on.. You don't need that...",
        inline=False)
    return welcome_embed


@bot.event
async def on_ready():
    logging.info("Joined as {0.name}".format(bot.user))
    global guild
    guild = await bot.fetch_guild(config.GuildId)
    channel: discord.TextChannel = [channel for channel in await guild.fetch_channels() if channel.id == config.welcomeChannelId][0]
    try:
        welcome_message: discord.Message = await channel.fetch_message(config.welcomeMessageId)
        await welcome_message.edit(content="",
                                   embed=create_welcome_embed(),
                                   view=InitExchange(config, bot))
    except discord.NotFound:
        await channel.send(embed=create_welcome_embed(),
                           view=InitExchange(config, bot))

    expired_channels = [channel for channel in await guild.fetch_channels()
                        if channel.category_id == config.hiddenCategoryId
                        and channel.type != discord.ChannelType.category]
    for channel in expired_channels:
        await channel.delete()


@bot.event
async def on_message(msg: discord.Message):
    if msg.author.id == bot.user.id:
        return
    if msg.channel.type != discord.ChannelType.text:
        return
    if msg.channel.category_id != config.hiddenCategoryId:
        return

    channels = await guild.fetch_channels()

    targetChannel: list[discord.TextChannel] = [channel for channel in channels if channel.name == msg.channel.topic]
    if targetChannel is None:
        logging.error("Didn't find channel {0}".format(msg.channel.topic))
        await msg.reply("Sorka, nejakej error")
        return

    webhook: list[discord.Webhook] = await targetChannel[0].webhooks()

    if len(webhook) == 0:
        name = "Hello there"
        webhook.append(await targetChannel[0].create_webhook(name=name))

    avatar = "https://cdn.discordapp.com/icons/914813122689241129/042d4c00a55cb2b2a8ef6d5db652b8df.png?size=96"
    content = escape_mentions(msg.content)
    files = []
    for attachment in msg.attachments:
        f = await attachment.to_file()
        files.append(f)
    await webhook[0].send(content, files=files, avatar_url=avatar)

    overwrite = {msg.author: discord.PermissionOverwrite(send_messages=False)}
    await msg.reply(content="Odesláno\nKanál se smaže za pár sekund :+1:", view=None)
    await msg.channel.edit(topic="Deleting...", overwrites=overwrite)
    await asyncio.sleep(10)
    await msg.channel.delete()

bot.run(token)
