# -*- coding: utf8 -*-
import logging

from discord.ext import commands

from dismock import say, TestResult

logger = logging.getLogger(__name__)


class Core(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="stats", aliases=['list'])
    async def stats(self, ctx: commands.context.Context):
        """List all the tests and their status"""
        bot = self.bot

        await bot.display_stats(ctx.channel)

    @commands.command(name="run")
    async def run(self, ctx: commands.context.Context, arg: str = None):
        """Run tests.
            all - Run all tests
            unrun - Run all tests that have not been run
            failed - Run all tests that have failed
            name - Run a specific test"""
        bot = self.bot
        name = arg
        channel = ctx.channel
        if name == 'all':
            await bot.run_by_predicate(ctx.channel, lambda t: True)
        elif name == 'unrun':
            pred = lambda t: t.result is TestResult.UNRUN
            await bot.run_by_predicate(ctx.channel, pred)
        elif name == 'failed':
            pred = lambda t: t.result is TestResult.FAILED
            await bot.run_by_predicate(ctx.channel, pred)
        elif not bot.tests.find_by_name(name):
            text = ':x: There is no test called `{}`'
            await channel.send(text.format(name))
        else:
            print('Running test:', name)
            await channel.send('Running test `{}`'.format(name))
            await bot.run_test(bot.tests.find_by_name(name), channel)
            await bot.display_stats(channel)


def setup(bot):
    bot.add_cog(Core(bot))
