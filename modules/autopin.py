from logging import Logger
from configparser import ConfigParser

import discord
from discord.ext import commands


class Autopin(discord.Cog):
    def __init__(self, bot: discord.Bot, logger: Logger, config: ConfigParser):
        self.bot = bot
        self.logger = logger
        self.threshold = config.getint("Autopin", "threshold")
        self.thread_threshold = config.getint("Autopin", "customThreadThreshold")
        self.emoji = config.get("Autopin", "emoji")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.emoji.name != self.emoji:
            return
        channel = await self.bot.fetch_channel(payload.channel_id)
        message: discord.Message = await channel.fetch_message(payload.message_id)
        if message.pinned:
            return
        threshold: int
        if self.thread_threshold > 0 and (channel.type == discord.ChannelType.public_thread
                                          or channel.type == discord.ChannelType.private_thread):
            threshold = self.thread_threshold
        else:
            threshold = self.threshold

        reactions: list = [reaction for reaction in message.reactions if reaction.emoji == self.emoji]

        if len(reactions) >= threshold:
            await message.pin()
