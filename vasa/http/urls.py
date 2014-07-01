from werkzeug.routing import Map, Rule

from .endpoints import index, webapp_files


def make_urls(settings):
    url_map = Map([
        Rule('/', endpoint=index),
        Rule('/_webapp/<path:path>', endpoint=webapp_files)
    ])

    return url_map.bind('localhost', '/')
