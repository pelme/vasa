import sys
import logging


def setup_logging(settings):
    logging.basicConfig(stream=sys.stdout,
                        level=logging.INFO,
                        format='[%(levelname)s %(asctime)s] %(message)s')
