
import aiohttp_jinja2
from aiohttp.web import Request, RouteTableDef
# from aiohttp_session import get_session
from app.func import default_context
from app.const import log

routes = RouteTableDef()

__all__ = (
    "routes",
)


@routes.get("/")
@aiohttp_jinja2.template("index.html")
async def index(request: Request) -> dict:

    ctx = await default_context(request)

    ctx.update(
        title=ctx["site_label"] + " — Официальный сайт.",
        is_index=True,
    )

    return ctx
