from logging import Logger
from configparser import ConfigParser

import discord


class Autopin(discord.Cog):
    """
    Automatically pins message if certain reaction count is reached
    """
    def __init__(self, bot: discord.Bot, logger: Logger, config: ConfigParser):
        self.bot = bot
        self.logger = logger
        self.modid = config.getint("Global", "modid")
        self.threshold = config.getint("Autopin", "threshold")
        self.thread_threshold = config.getint("Autopin", "customThreadThreshold")
        self.lockemoji = config.get("Autopin", "lockemoji")
        self.emoji = config.get("Autopin", "emoji")

    @discord.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.emoji.name != self.emoji and payload.emoji.name != self.lockemoji:
            return
        channel = await self.bot.fetch_channel(payload.channel_id)
        message: discord.Message = await channel.fetch_message(payload.message_id)
        is_admin: bool = len(list(filter(lambda role: role.id == self.modid, payload.member.roles))) > 0
        if payload.emoji.name == self.lockemoji:
            if is_admin and message.pinned:
                await message.unpin()
            return

        if message.pinned:
            return

        lock_reactions = [reaction for reaction in message.reactions if reaction.emoji == self.lockemoji]
        if len(lock_reactions) > 0:
            for user in await lock_reactions[0].users().flatten():
                if len([role for role in user.roles if role.id == self.modid]) > 0:
                    return

        threshold: int
        if self.thread_threshold > 0 and (channel.type == discord.ChannelType.public_thread
                                          or channel.type == discord.ChannelType.private_thread):
            threshold = self.thread_threshold
        else:
            threshold = self.threshold

        reaction: discord.Reaction = [reaction for reaction in message.reactions if reaction.emoji == self.emoji][0]

        if reaction.count >= threshold:
            await message.pin()
