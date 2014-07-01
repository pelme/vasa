import asyncio
import functools
import logging

from .handler import HttpRequestHandler

from .urls import make_urls

logger = logging.getLogger(__name__)


def make_http_protocol_factory(settings, loop=None):
    # logger.info('Running HTTP server on http://%s:%d' % (settings.host, settings.port))

    if loop is None:
        loop = asyncio.get_event_loop()

    urls = make_urls(settings)

    return functools.partial(HttpRequestHandler,
                             urls=urls,
                             settings=settings,
                             debug=True, keep_alive=30, loop=loop)
