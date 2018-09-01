""" Dismock is a small library designed to help with the
    creation of bots to test other bots. This is currently
    part of the MathBot project but if it gains enough
    traction I might fork it into its own repository
    Interfacing with the bot through discord:

    ::stats
        Gives details about which tests have been
        run and what the results were

    ::run test_name
        Run a particular test

    ::run all
        Run all tests

    ::run unrun
        Run all tests that have not yet been run

    ::run failed
        Run all tests that failed on the most recent run

"""

import logging
import sys
import traceback

import discord
from discord.ext import commands

from dismock.models import TestResult, TestRequirementFailure, Test
from dismock.test_classes import Interface, TestCollector

logger = logging.getLogger(__name__)
initial_extensions = (
    'dismock.cogs.core',
    'dismock.cogs.admin',
)


class DiscordBot(commands.AutoShardedBot):
    """ Discord bot used to run tests.
        This class by itself does not provide any useful methods for human interaction.
    """

    def __init__(self, command_prefix, target_name: str) -> None:
        super().__init__(command_prefix)
        self._target_name = target_name.lower()

        for extension in initial_extensions:
            try:
                self.load_extension(extension)
                logger.info(f'Loaded extension {extension}.')
            except Exception:
                logger.error(f'Failed to load extension {extension}.', file=sys.stderr)
                traceback.print_exc()

    # self._setup_done = False

    def _find_target(self, guild: discord.Guild) -> discord.User:
        for i in guild.members:
            if self._target_name in i.name.lower():
                return i
        raise KeyError('Could not find memory with name {}'.format(self._target_name))

    async def run_test(self,
                       test: Test,
                       channel: discord.TextChannel,
                       stop_error: bool = False) -> TestResult:
        """ Run a single test in a given channel.
            Updates the test with the result, and also returns it.
        """
        interface = Interface(
            self,
            channel,
            self._find_target(channel.guild))
        try:
            await test.func(interface)
        except TestRequirementFailure:
            test.result = TestResult.FAILED
            if not stop_error:
                raise
        else:
            test.result = TestResult.SUCCESS
        return test.result


class DiscordUI(DiscordBot):
    """ A variant of the discord bot which supports additional commands
        to allow a human to also interact with it.
    """

    def __init__(self, target_name: str, tests: TestCollector, command_prefix='::') -> None:
        super().__init__(target_name=target_name, command_prefix=command_prefix)
        self.tests = tests

    async def run_by_predicate(self, channel, predicate):
        for test in self.tests:
            if predicate(test):
                await channel.send('**Running test {}**'.format(test.name))
                await self.run_test(test, channel, stop_error=True)

    async def display_stats(self, channel: discord.TextChannel) -> None:
        """ Display the status of the various tests. """
        # NOTE: An emoji is the width of two spaces
        response = '```\n'
        longest_name = max(map(lambda t: len(t.name), self.tests))
        for test in self.tests:
            response += test.name.rjust(longest_name) + ' '
            if test.needs_human:
                response += '✋ '
            else:
                response += '   '
            if test.result is TestResult.UNRUN:
                response += '⚫ Not run\n'
            elif test.result is TestResult.SUCCESS:
                response += '✔️ Passed\n'
            elif test.result is TestResult.FAILED:
                response += '❌ Failed\n'
        response += '```\n'
        await channel.send(response)

    async def on_ready(self) -> None:
        """ Report when the bot is ready for use """
        logger.info('Started dismock bot.')
        logger.info('Available tests are:')
        for i in self.tests:
            logger.info('   {}'.format(i.name))

    async def on_message(self, message: discord.Message) -> None:
        """ Handle an incomming message """
        channel = message.channel
        if isinstance(channel, discord.TextChannel):
            await self.process_commands(message)


async def say(channel, message=None, embed=None, image=None):
    """ Wrapper function for various sending methods

    :param discord.Channel channel: Channel where to send the content
    :param str message: (optional) actual message to be sent
    :param discord.Embed embed: (optional) embed message to be sent
    :param str image: (optional) file path to an image to be sent
    """
    if embed:
        await channel.send(embed=embed)
    elif image and message:
        await channel.send(message, file=discord.File(image, image))
    elif image and not message:
        await channel.send(file=discord.File(image, image))
    else:
        await channel.send(message)


def run_interactive_bot(target_name, token, test_collector):
    bot = DiscordUI(target_name, test_collector, command_prefix='::')
    bot.run(token)
