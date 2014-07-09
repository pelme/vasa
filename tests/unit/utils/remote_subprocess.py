import asyncio

from vasa.utils.remote_subprocess import create_remote_subprocess_exec


@asyncio.coroutine
def test_simple(loop, gateway):
    proc = yield from create_remote_subprocess_exec(
        'echo', 'tjosan',
        gateway=gateway,
        loop=loop)

    assert (yield from proc.wait()) == 0
    assert (yield from proc.stdout.read()) == b'tjosan\n'
    assert (yield from proc.stderr.read()) == b''
