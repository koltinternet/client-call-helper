from aiohttp import web


def setup_routes(app: web.Application) -> None:

    from .common import routes
    app.add_routes(routes)