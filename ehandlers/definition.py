from typing import Callable, Awaitable

import aiohttp_jinja2
from aiohttp.web import Application, Request, Response
from aiohttp import web
from app.const import log


async def handle_404(request: web.Request) -> Response:
    ctx = dict(
        title="Страница не найдена",
        code=404,
        body="<p>Такой страницы не существует.</p><br>"
             "<p>Вернитесь назад по истории, или "
             "<a href='/'>перейдите на главную страницу</a></p>",
    )

    return aiohttp_jinja2.render_template(
        "errors/template.html",
        request=request,
        context=ctx,
        status=404
    )


async def handle_500(request: web.Request) -> Response:
    ctx = dict(
        title="У нас неполадка",
        code=500,
        body="<p>Нам очень жаль. Случилось неприятное, невероятное.</p>"
             "<p>Мы пока не знаем, что это такое, но в скором времени "
             "это станет известно администратору.</p>"
             "<p>Попробуйте перезагрузить страницу или вернуться на главную.</p>"
             "<a href='/'>Перейти на главную страницу</a><br>",
    )

    return aiohttp_jinja2.render_template(
        "errors/template.html",
        request=request,
        context=ctx,
        status=500
    )


def create_error_middleware(overrides: dict[int, Callable[[Request], Awaitable[Response]]]) -> Callable:
    @web.middleware
    async def error_middleware(request: Request, handler: Callable[[Request], Awaitable[Response]]) -> Response:
        try:
            return await handler(request)
        except web.HTTPException as ex:
            override = overrides.get(ex.status)
            if override:
                return await override(request)
            raise
        except Exception:
            log.opt(exception=True, colors=False).error("Unhandled exception:")
            return await overrides[500](request)

    return error_middleware


def setup_error_handlers(app: Application) -> None:
    error_middleware = create_error_middleware({
        404: handle_404,
        500: handle_500,
    })
    app.middlewares.append(error_middleware)
