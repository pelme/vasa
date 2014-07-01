import pytest
import asyncio

from vasa.http.server import make_http_protocol_factory


@pytest.fixture
def loop():
    return asyncio.get_event_loop()


class Server:
    def __init__(self, server):
        self._server = server

    @property
    def _socket(self):
        return self._server.sockets[0]

    @property
    def host(self):
        return 'localhost'
        return self._socket.getsockname()[0]

    @property
    def port(self):
        return self._socket.getsockname()[1]

    @property
    def url(self):
        return 'http://%s:%s' % (self.host, self.port)


@pytest.fixture
def webapp_root(tmpdir):
    dir = tmpdir.join('webapp_root')
    dir.ensure_dir()
    return dir


@pytest.yield_fixture
def server(loop, webapp_root):
    static_root_dir = str(webapp_root)

    class Settings:
        webapp_root = static_root_dir

    proto_factory = make_http_protocol_factory(Settings())
    coro = loop.create_server(proto_factory, host='localhost', port=12345)
    server = loop.run_until_complete(coro)
    yield Server(server)
    server.close()


import aiohttp


@asyncio.coroutine
def test_simple_static_file(webapp_root, server):
    FILE_CONTENTS = b'foobar'
    webapp_root.join('foo.txt').write(FILE_CONTENTS)

    response = yield from aiohttp.request('GET', server.url + '/_webapp/foo.txt')

    assert response.status == 200
    body = yield from response.read_and_close()
    assert body == FILE_CONTENTS


@asyncio.coroutine
def test_non_existent_file(server):
    response = yield from aiohttp.request('GET', server.url + '/_webapp/noope.txt')
    assert response.status == 404


@asyncio.coroutine
def test_directory_traversal_error(server):
    response = yield from aiohttp.request('GET', server.url + '/_webapp/../../../../../../../../../../../../../../../../../etc/passwd')
    assert response.status == 404


@asyncio.coroutine
def test_content_type(server, webapp_root):
    filename = 'foo.png'
    webapp_root.join(filename).write(b'kaka')
    response = yield from aiohttp.request('GET', server.url + '/_webapp/%s' % filename)
    assert response.status == 200
    assert response.get_content_type() == 'image/png'


@asyncio.coroutine
def test_index(server, webapp_root):
    webapp_root.join('index.html').write('Hello, world')

    response = yield from aiohttp.request('GET', server.url + '/')

    assert response.get_content_type() == 'text/html'
    body = yield from response.read_and_close()
    assert body == b'Hello, world'
