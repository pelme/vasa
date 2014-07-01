import asyncio
import mimetypes
from pathlib import Path

from .response import DataResponse, ResponseNotFound


@asyncio.coroutine
def index(request, writer, settings):
    full_path = (Path(settings.webapp_root) / 'index.html').resolve()

    with full_path.open('rb') as f:
        return DataResponse(writer, data=f.read(), content_type='text/html')


@asyncio.coroutine
def webapp_files(request, writer, settings, path):
    try:
        full_path = (Path(settings.webapp_root) / path).resolve()
    except FileNotFoundError:
        return ResponseNotFound(writer)

    if not str(full_path).startswith(settings.webapp_root):
        return ResponseNotFound(writer)

    try:
        with full_path.open('rb') as f:
            contents = f.read()

    except FileNotFoundError:
        return ResponseNotFound(writer)
    else:
        (content_type, encoding) = mimetypes.guess_type(str(full_path))
        content_type = content_type or 'application/octet-stream'

        return DataResponse(writer, data=contents, content_type=content_type)
