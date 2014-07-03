import asyncio
import logging

import execnet

logger = logging.getLogger(__name__)


def reverse_some_text(channel):
    import socket

    while 1:
        thing = channel.receive()
        channel.send('[%s] reversed text: %s' % (
            socket.gethostname(),
            ''.join(reversed(thing)),
        ))


class Minion:
    def __init__(self, host_string, provides=()):
        self.host_string = host_string
        self.provides = provides
        self._gw = None

    @asyncio.coroutine
    def execute_steps(self, loop, steps):
        if self._gw is None:
            self._gw = execnet.makegateway('ssh=%s' % self.host_string)

        channel = self._gw.remote_exec(reverse_some_text)
        channel.send('sent from the master')

        result = yield from loop.run_in_executor(None, channel.receive)

        logger.info('Recieved the result: %s' % result)
