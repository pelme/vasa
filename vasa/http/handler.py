import asyncio
import aiohttp
import aiohttp.server
import logging

from werkzeug.exceptions import NotFound


logger = logging.getLogger(__name__)


class HttpRequestHandler(aiohttp.server.ServerHttpProtocol):

    def __init__(self, *args, **kwargs):
        self.urls = kwargs.pop('urls')
        self.settings = kwargs.pop('settings')
        super().__init__(*args, **kwargs)

    @asyncio.coroutine
    def handle_request(self, message, payload):
        logger.info('method = {!r}; path = {!r}; version = {!r}'.format(message.method,
                                                                        message.path,
                                                                        message.version))

        try:
            endpoint, args = self.urls.match(message.path)
            response = yield from endpoint(message, self.writer, self.settings, **args)

            transmit = getattr(response, 'transmit', lambda: None)
            transmit()

        except NotFound:
            raise aiohttp.HttpErrorException(404)


def make_handler(*args, **kwargs):
    return lambda: HttpRequestHandler(*args, **kwargs)
