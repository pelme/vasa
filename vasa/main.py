import asyncio
import pathlib
import logging

logger = logging.getLogger(__name__)

from . import __version__
from .http.server import make_http_protocol_factory
from .logging import setup_logging


from vasa.minions import Minion


class Settings:
    http_host = '127.0.0.1'
    http_port = 3000
    webapp_root = str((pathlib.Path('.') / 'webapp_dist').resolve())
    minions = [
        Minion('andreas@lingon.pelme.se'),
    ]

    def _verify(self):
        assert pathlib.Path(self.webapp_root).is_absolute()


def main():
    # TODO: Configure this in a better way :)
    settings = Settings()
    settings._verify()

    setup_logging(settings)

    logger.info('Vasa v%s, starting...' % __version__)

    asyncio.set_event_loop(None)
    loop = asyncio.new_event_loop()

    loop.run_until_complete(loop.create_server(make_http_protocol_factory(settings, loop=loop),
                                               host=settings.http_host,
                                               port=settings.http_port))

    loop.call_soon(logger.info, 'Accepting HTTP connections on http://%s:%s' % (settings.http_host,
                                                                                settings.http_port))

    @asyncio.coroutine
    def jobchecker():
        minion = settings.minions[0]

        while 1:
            logger.info('Sending a job to a minion...')
            yield from minion.execute_steps(loop, ['somestep'])
            yield from asyncio.sleep(1)

    asyncio.async(jobchecker())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info('Keyboardinterrupt - quitting')


if __name__ == '__main__':
    main()
