import pytest
import asyncio

import execnet


def pytest_pyfunc_call(__multicall__, pyfuncitem):
    coro = pyfuncitem.obj

    if asyncio.iscoroutinefunction(coro):
        funcargs = pyfuncitem.funcargs
        testargs = {arg: funcargs[arg] for arg in pyfuncitem._fixtureinfo.argnames}

        loop = funcargs['loop']
        loop.run_until_complete(coro(**testargs))


def pytest_pycollect_makeitem(__multicall__, collector, name, obj):
    if asyncio.iscoroutinefunction(obj) and obj.__name__.lower().startswith('test'):
        return list(collector._genfunctions(name, obj))


@pytest.yield_fixture
def loop():

    old = asyncio.get_event_loop()
    asyncio.set_event_loop(None)
    yield asyncio.new_event_loop()
    asyncio.set_event_loop(old)


REMOTE_PYTHONS = [
    'python2.5',
    'python2.6',
    'python2.7',
    'python3.1',
    'python3.2',
    'python3.3',
    'python3.4',
    # 'pypy',
]


@pytest.fixture(params=REMOTE_PYTHONS)
def gateway(request):
    try:
        gw = execnet.makegateway('popen//python=%s' % request.param)
    except FileNotFoundError:
        pytest.skip('%s is not installed')

    gw.reconfigure(py2str_as_py3str=False, py3str_as_py2str=False)
    return gw
