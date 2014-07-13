import asyncio
import functools
import logging

from .handler import HttpRequestHandler

from .urls import make_urls

logger = logging.getLogger(__name__)


def make_http_protocol_factory(settings, loop):

    logger.info('Accepting HTTP connections on http://%s:%s' % (
        settings.http_host, settings.http_port))

    urls = make_urls(settings)

    return functools.partial(HttpRequestHandler,
                             urls=urls,
                             settings=settings,
                             debug=True, keep_alive=30, loop=loop)
