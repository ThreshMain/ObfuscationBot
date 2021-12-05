import json
import logging


class Config:

    channelMap: dict[str, int]
    listeningChannel: int
    sourceLink: str
    GuildId: int
    welcomeMessage: int

    def __init__(self, logger: logging.Logger):
        with open("./config.json", 'r') as fp:
            file = fp.read()

        procesInput = json.loads(file)
        self.channelMap = procesInput["channelMapping"]
        self.listeningChannel = procesInput["listeningChannel"]
        self.sourceLink = procesInput["sourceLink"]
        self.GuildId = procesInput["GuildId"]
        self.welcomeMessage = procesInput["welcomeMessage"]

        logger.info("Loaded config")
