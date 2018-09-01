import contextlib
import logging
import os
import sys


@contextlib.contextmanager
def setup_logging():
    logger = logging.getLogger()
    try:
        if os.environ["DEBUG"]:
            logger.setLevel(logging.DEBUG)
    except KeyError:
        logger.setLevel(logging.INFO)
    try:
        # __enter__
        logging.getLogger('discord').setLevel(logging.INFO)
        logging.getLogger('discord.http').setLevel(logging.WARN)
        logging.getLogger('websockets').setLevel(logging.WARN)
        logging.getLogger('urllib3').setLevel(logging.WARN)
        logging.getLogger('asyncio').setLevel(logging.WARN)

        # if not os.path.exists("log/"):  # Check if the directory exists
        #     os.makedirs("log/")  # Create it if not
        # log_filename = 'log/bot_{}.log'.format(time.strftime("%Y%m%d-%H%M%S"))
        # f_handler = logging.FileHandler(filename=log_filename, encoding='utf-8', mode='w')
        s_handler = logging.StreamHandler(stream=sys.stdout)
        dt_fmt = '%Y-%m-%d %H:%M:%S'
        fmt = logging.Formatter(
            '%(asctime)s %(levelname)-5.5s [%(name)s] [%(funcName)s()] %(message)s <line %(lineno)d>',
            dt_fmt,
            style='%')

        # for handler in [f_handler, s_handler]:
        for handler in [s_handler]:
            handler.setFormatter(fmt)
            logger.addHandler(handler)

        yield
    finally:
        # __exit__
        handlers = logger.handlers[:]
        for hdlr in handlers:
            hdlr.close()
            logger.removeHandler(hdlr)
