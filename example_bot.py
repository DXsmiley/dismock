'''
    Run with:
        python example_bot.py
    Enter token in config.json under DISMOCK_BOT_TOKEN
'''
import json
import logging

import discord
from discord.ext import commands

from hl_utils import setup_logging

logger = logging.getLogger(__name__)


class DiscordBot(commands.AutoShardedBot):

    def __init__(self, command_prefix, **options):
        # DISCORD VARIABLES
        super().__init__(command_prefix, **options)
        self.actions = {}
        self.token = None

        # GENERAL VARIABLES
        self.prompt = command_prefix
        self.username = None

    async def on_ready(self):
        logger.info('Ready')

    async def on_message(self, message: discord.Message):
        channel: discord.TextChannel = message.channel
        if message.content == 'ping?':
            logger.info('Replying')
            await channel.send('pong!')

    def run(self, token):
        self.token = token
        try:
            super().run(self.token, reconnect=True)
        except:
            pass


if __name__ == '__main__':
    with setup_logging():
        bot = DiscordBot(command_prefix=':;')

        with open('config.json') as f:
            config = json.load(f)
        bot.run(config['DISMOCK_BOT_TOKEN'])
