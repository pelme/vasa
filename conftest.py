import asyncio


def pytest_pyfunc_call(__multicall__, pyfuncitem):
    coro = pyfuncitem.obj

    if asyncio.iscoroutinefunction(coro):
        funcargs = pyfuncitem.funcargs
        testargs = {arg: funcargs[arg] for arg in pyfuncitem._fixtureinfo.argnames}

        loop = asyncio.get_event_loop()
        loop.run_until_complete(coro(**testargs))


def pytest_pycollect_makeitem(__multicall__, collector, name, obj):
    if asyncio.iscoroutinefunction(obj):
        return list(collector._genfunctions(name, obj))
