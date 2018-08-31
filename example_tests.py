"""
    Run with:
        python example_tests.py TARGET_NAME TESTER_TOKEN
"""
import json
import logging
import sys

# The tests themselves
import dismock.test_classes
from hl_utils import setup_logging

logger = logging.getLogger(__name__)
testcollector = dismock.test_classes.TestCollector()


@testcollector()
async def test_ping(interface):
    await interface.assert_reply_equals('ping?', 'pong!')


# Make it easy to run the tests

if __name__ == '__main__':
    with setup_logging():
        with open('config.json') as f:
            config = json.load(f)
        token = config['TESTED_BOT_TOKEN']
        target_name = config['TESTED_BOT_NAME']
        dismock.run_interactive_bot(target_name, token, testcollector)