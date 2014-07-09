import asyncio

from ._remote_subprocess_remote import STDOUT, STDERR, RETURN_CODE
from . import _remote_subprocess_remote


class RemoteProcess:
    "Implements a subset of asyncio.subprocess.Process"

    returncode = None

    def __init__(self, return_future, stdout, stderr):
        self._return_future = return_future
        self.stdout = stdout
        self.stderr = stderr

    @classmethod
    def with_loop(cls, loop):
        return cls(return_future=asyncio.Future(loop=loop),
                   stdout=asyncio.StreamReader(loop=loop),
                   stderr=asyncio.StreamReader(loop=loop))

    def _set_returncode(self, ret):
        self.returncode = ret
        self._return_future.set_result(ret)

    @asyncio.coroutine
    def wait(self):
        return (yield from self._return_future)


@asyncio.coroutine
def _loop(channel, proc, loop):
    while 1:
        message, payload = (yield from loop.run_in_executor(None, channel.receive))

        if message == STDOUT:
            proc.stdout.feed_data(payload)

        if message == STDERR:
            proc.stderr.feed_data(payload)

        if message == RETURN_CODE:
            proc.stdout.feed_eof()
            proc.stderr.feed_eof()
            proc._set_returncode(payload)
            return


@asyncio.coroutine
def create_remote_subprocess_exec(*args, loop, gateway):
    """
    Works like asyncio.create_subprocess_exec, but launches the subprocess on
    the execnet `gateway`.
    """

    channel = gateway.remote_exec(_remote_subprocess_remote)
    channel.send(args)

    proc = RemoteProcess.with_loop(loop)
    asyncio.Task(_loop(channel, proc, loop))

    return proc
