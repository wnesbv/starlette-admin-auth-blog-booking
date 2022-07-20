
from sqlalchemy import select, update as sqlalchemy_update, delete

from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.storage_config import engine, async_session

from .models import MessageChat


templates = Jinja2Templates(directory="templates")


async def chat_update(
    request
):
    id = request.path_params["id"]
    template = "/chat/update.html"
    owner_chat = request.user.user_id

    async with async_session() as session:

        if request.method == "GET":
            result = await session.execute(
                select(MessageChat).where(MessageChat.id==id)
            )
            detail = result.scalars().first()

            if detail.owner_chat == owner_chat:

                return templates.TemplateResponse(
                    template,
                    {
                        "request": request,
                        "detail": detail,
                    },
                )
            return PlainTextResponse(
                "this is not your message..!"
            )

        #...
        if request.method == "POST":

            result = await session.execute(
                select(MessageChat).where(MessageChat.id == id)
            )
            detail = result.scalars().first()

            form = await request.form()

            detail.message = form["message"]

            # ...
            file_query = (
                sqlalchemy_update(MessageChat)
                .where(MessageChat.id == id)
                .values(form)
                .execution_options(synchronize_session="fetch")
            )

            await session.execute(file_query)
            await session.commit()

            context = {
                "request": request,
                "detail": detail,
            }

            response = templates.TemplateResponse(template, context)
            response = RedirectResponse(
                f"/chat/group/{ detail.owner_group }",
                status_code=302,
            )
            return response

    await engine.dispose()


async def chat_delete(
    request
):
    id = request.path_params["id"]
    template = "/chat/delete.html"
    owner_chat = request.user.user_id

    async with async_session() as session:

        if request.method == "GET":
            result = await session.execute(
                select(MessageChat).where(MessageChat.id==id)
            )
            detail = result.scalars().first()

            if detail.owner_chat == owner_chat:
                return templates.TemplateResponse(
                    template,
                    {
                        "request": request,
                        "id": id,
                        "detail": detail,
                    },
                )
            return PlainTextResponse(
                "this is not your message..!"
            )

        #...
        if request.method == "POST":

            form = await request.form()

            query = (
                delete(MessageChat).where(MessageChat.id == id)
            )
            await session.execute(query)
            await session.commit()

            context = {
                "request": request,
                "form": form,
            }

            response = templates.TemplateResponse(template, context)
            response = RedirectResponse(
                "/chat/group/list",
                status_code=302,
            )

            return response
        return templates.TemplateResponse(template, {"request": request})

    await engine.dispose()
