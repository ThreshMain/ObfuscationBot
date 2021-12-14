import json
import logging


class Config:

    sourceLink: str
    GuildId: int
    welcomeChannelId: int
    welcomeMessageId: int
    hiddenCategoryId: int
    studyCategoryId: int

    def __init__(self, logger: logging.Logger):
        with open("./config.json", 'r') as fp:
            file = fp.read()

        procesInput = json.loads(file)
        self.sourceLink = procesInput["sourceLink"]
        self.GuildId = procesInput["GuildId"]
        self.welcomeChannelId = procesInput["welcomeChannelId"]
        self.welcomeMessageId = procesInput["welcomeMessageId"]
        self.hiddenCategoryId = procesInput["hiddenCategoryId"]
        self.studyCategoryId = procesInput["studyCategoryId"]

        logger.info("Loaded config")
