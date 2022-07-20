
import uvicorn

from sqlalchemy.future import select

from starlette.middleware import Middleware
from starlette.applications import Starlette
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from routes.urls import routes

from db_config.storage_config import engine, async_session
from db_config.settings import settings

from account.models import User
from middleware import JWTAuthenticationBackend

#...
#from db_startup.db import on_app_startup
#...


templates = Jinja2Templates(directory="templates")

app = Starlette(
    debug=settings.DEBUG,
    routes=routes,
    #...
    #on_startup=[on_app_startup],
    # on_shutdown=[on_app_shutdown],
    #...
    middleware=[
        Middleware(
            AuthenticationMiddleware,
            backend=JWTAuthenticationBackend(
                secret_key=str(settings.SECRET_KEY),
                algorithm=settings.JWT_ALGORITHM,
                prefix=settings.JWT_PREFIX,
            ),
        ),
    ],
)


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.route("/")
async def homepage(
    request
):
    template = "index.html"

    async with async_session() as session:

        if not request.user.is_authenticated:
            response = templates.TemplateResponse(
                template, {"request": request}
            )
            return response
        result = await session.execute(
            select(User)
            .where(User.id==request.user.user_id)
        )
        odj_list = result.scalars().all()

        context = {
            "request": request,
            "odj_list": odj_list,
        }
        return templates.TemplateResponse(template, context)
    await engine.dispose()


@app.route("/details/{id:int}")
async def details(
    request
):

    id = request.path_params["id"]
    template = "details.html"

    async with async_session() as session:
        result = await session.execute(
            select(User)
            .where(User.id==id)
            .where(User.id==request.user.user_id)
        )
        detail = result.scalars().first()
        context = {
            "request": request,
            "detail": detail,
        }
        return templates.TemplateResponse(template, context)
    await engine.dispose()


@app.route("/error")
async def error(
    request
):

    raise RuntimeError("Oh no")


@app.exception_handler(404)
async def not_found(
    request, exc
):

    template = "404.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context, status_code=404)


@app.exception_handler(500)
async def server_error(
    request, exc
):

    template = "500.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context, status_code=500)


if __name__ == "__main__":

    uvicorn.run(app, host="127.0.0.1", port=8000, debug=settings.DEBUG)
