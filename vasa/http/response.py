import functools

import aiohttp


class DataResponse(aiohttp.Response):
    def __init__(self, writer, *,
                 data,
                 content_type,
                 status=200):
        super().__init__(writer, status)
        self._content_type = content_type
        self._data = data

    def transmit(self):
        self.add_headers(('Content-type', self._content_type),
                         ('Content-length', str(len(self._data))))
        self.send_headers()
        self.write(self._data)


ResponseNotFound = functools.partial(DataResponse,
                                     status=404,
                                     content_type='text/plain',
                                     data=b'Not found')
