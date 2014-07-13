import pytest
import asyncio

from vasa.http.server import make_http_protocol_factory

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
        http_host = 'localhost'
        http_port = 12345
        webapp_root = static_root_dir

    settings = Settings()

    proto_factory = make_http_protocol_factory(settings, loop=loop)
    coro = loop.create_server(proto_factory, host=settings.http_host, port=settings.http_port)
    server = loop.run_until_complete(coro)
    yield Server(server)
    server.close()


import aiohttp


@asyncio.coroutine
def test_simple_static_file(loop, webapp_root, server):
    FILE_CONTENTS = b'foobar'
    webapp_root.join('foo.txt').write(FILE_CONTENTS)

    response = yield from aiohttp.request('GET', server.url + '/_webapp/foo.txt',
                                          loop=loop)

    assert response.status == 200
    body = yield from response.read_and_close()
    assert body == FILE_CONTENTS


@asyncio.coroutine
def test_non_existent_file(loop, server):
    response = yield from aiohttp.request('GET', server.url + '/_webapp/noope.txt',
                                          loop=loop)
    assert response.status == 404


@asyncio.coroutine
def test_directory_traversal_error(loop, server):
    url = server.url + '/_webapp/../../../../../../../../../../../../../../../../../etc/passwd'
    response = yield from aiohttp.request('GET', url, loop=loop)
    assert response.status == 404


@asyncio.coroutine
def test_content_type(loop, server, webapp_root):
    filename = 'foo.png'
    webapp_root.join(filename).write(b'kaka')
    response = yield from aiohttp.request('GET', server.url + '/_webapp/%s' % filename, loop=loop)
    assert response.status == 200
    assert response.get_content_type() == 'image/png'


@asyncio.coroutine
def test_index(loop, server, webapp_root):
    webapp_root.join('index.html').write('Hello, world')

    response = yield from aiohttp.request('GET', server.url + '/', loop=loop)

    assert response.get_content_type() == 'text/html'
    body = yield from response.read_and_close()
    assert body == b'Hello, world'
