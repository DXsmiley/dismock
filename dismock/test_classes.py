import asyncio
import re

import discord

from dismock.models import NoReactionError, NoResponseError, ResponseDidNotMatchError, ReactionDidNotMatchError, \
    UnexpectedResponseError, HumanResponseTimeout, HumanResponseFailure, Test

TIMEOUT = 20


class Interface:
    """ The interface that the test functions should use to interface with discord.
        Test functions should not access the discord.py client directly.
    """

    def __init__(self,
                 client: discord.Client,
                 channel: discord.TextChannel,
                 target: discord.User) -> None:
        self.client = client  # The discord.py client object
        self.channel = channel  # The channel the test is running in
        self.target = target  # The bot which we are testing

    async def send_message(self, content):
        """ Send a message to the testing channel. """
        return await self.channel.send( content)

    async def edit_message(self, message: discord.Message, new_content):
        """ Modified a message. Doesn't actually care what this message is. """
        return await message.edit(content=new_content)

    async def wait_for_reaction(self, message):
        def check(reaction, user):
            return (
                    reaction.message.id == message.id
                    and user == self.target
                    and reaction.message.channel == self.channel)

        result = await self.client.wait_for('reaction_add', timeout=TIMEOUT, check=check)
        if result is None:
            raise NoReactionError
        return result

    async def wait_for_message(self):
        """ Waits for the bot the send a message.
            If the bot takes longer than {} seconds, the test fails.
        """.format(TIMEOUT)

        def check(m: discord.Message):
            return m.author == self.target and m.channel == self.channel

        result = await self.client.wait_for(
            'message',
            timeout=TIMEOUT,
            check=check)
        if result is None:
            raise NoResponseError
        return result

    async def wait_for_reply(self, content):
        """ Sends a message and returns the next message that the targeted bot sends. """
        await self.send_message(content)
        return await self.wait_for_message()

    async def assert_message_equals(self, matches):
        """ Waits for the next message.
            If the message does not match a string exactly, fail the test.
        """
        response = await self.wait_for_message()
        if response.content != matches:
            raise ResponseDidNotMatchError
        return response

    async def assert_message_contains(self, substring):
        """ Waits for the next message.
            If the message does not contain the given substring, fail the test.
        """
        response = await self.wait_for_message()
        if substring not in response.content:
            raise ResponseDidNotMatchError
        return response

    async def assert_message_matches(self, regex):
        """ Waits for the next message.
            If the message does not match a regex, fail the test.
        """
        response = await self.wait_for_message()
        if not re.match(regex, response.content):
            raise ResponseDidNotMatchError
        return response

    async def assert_reply_equals(self, contents, matches):
        """ Send a message and wait for a response.
            If the response does not match a string exactly, fail the test.
        """
        # print('Sending...')
        await self.send_message(contents)
        # print('About to wait...')
        response = await self.wait_for_message()
        # print('Got response')
        if response.content != matches:
            raise ResponseDidNotMatchError
        return response

    async def assert_reply_contains(self, contents, substring):
        """ Send a message and wait for a response.
            If the response does not contain the given substring, fail the test.
        """
        await self.send_message(contents)
        response = await self.wait_for_message()
        if substring not in response.content:
            raise ResponseDidNotMatchError
        return response

    async def assert_reply_matches(self, contents, regex):
        """ Send a message and wait for a response.
            If the response does not match a regex, fail the test.
        """
        await self.send_message(contents)
        response = await self.wait_for_message()
        if not re.match(regex, response.content):
            raise ResponseDidNotMatchError
        return response

    async def assert_reaction_equals(self, contents, emoji):
        reaction = await self.wait_for_reaction(await self.send_message(contents))
        if str(reaction.emoji) != emoji:
            raise ReactionDidNotMatchError
        return reaction

    async def ensure_silence(self):
        """ Ensures that the bot does not post any messages for some number of seconds. """

        def check(m: discord.Message):
            return m.author == self.target and m.channel == self.channel

        result = await self.client.wait_for(
            'message',
            timeout=TIMEOUT,
            check=check)
        if result is not None:
            raise UnexpectedResponseError

    async def ask_human(self, query):
        """ Asks a human for an opinion on a question. Currently, only yes-no questions
            are supported. If the human answers 'no', the test will be failed.
        """
        message: discord.Message = await self.channel.send(query)
        await message.add_reaction(u'\u2714')
        await message.add_reaction(u'\u274C')
        await asyncio.sleep(0.5)

        def check(reaction: discord.Reaction, user: discord.User):
            return reaction.message == message
        reaction = await self.client.wait_for('reaction_add', timeout=TIMEOUT, check=check)
        if reaction is None:
            raise HumanResponseTimeout
        reaction, _ = reaction
        if reaction.emoji == u'\u274C':
            raise HumanResponseFailure


class ExpectCalls:  # pylint: disable=too-few-public-methods

    """ Wrap a function in an object which counts the number
        of times it was called. If the number of calls is not
        equal to the expected number when this object is
        garbage collected, something has gone wrong, and in
        that case an error is thrown.
    """

    def __init__(self, function, expected_calls=1):
        self.function = function
        self.expected_calls = expected_calls
        self.call_count = 0

    def __call__(self, *args, **kwargs):
        self.call_count += 1
        return self.function(*args, **kwargs)

    def __del__(self):
        if self.call_count != self.expected_calls:
            message = '{} was called {} times. It was expcted to have been called {} times'
            raise RuntimeError(message.format(self.function, self.call_count, self.expected_calls))


class TestCollector:
    """ Used to group tests and pass them around all at once. """

    def __init__(self):
        self._tests = []

    def add(self, function, name: str = '', needs_human: bool = False):
        """ Adds a test function to the group. """
        name = name or function.__name__
        test = Test(name, function, needs_human=needs_human)
        if name in self._tests:
            raise KeyError('A test case called {} already exists.'.format(name))
        self._tests.append(test)

    def find_by_name(self, name: str):
        """ Return the test with the given name.
            Return None if it does not exist.
        """
        for i in self._tests:
            if i.name == name:
                return i
        return None

    def __call__(self, *args, **kwargs):
        """ Add a test decorator-style. """

        def _decorator(function):
            self.add(function, *args, **kwargs)

        return ExpectCalls(_decorator, 1)

    def __iter__(self):
        return (i for i in self._tests)