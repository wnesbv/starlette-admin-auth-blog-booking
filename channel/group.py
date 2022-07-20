
from sqlalchemy import select, update as sqlalchemy_update, delete

from starlette.authentication import requires
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.storage_config import engine, async_session

from .models import MessageChat, GroupChat


templates = Jinja2Templates(directory="templates")


async def group_list(
    request
):

    template = "/group/list.html"

    async with async_session() as session:

        result = await session.execute(
            select(GroupChat).order_by(GroupChat.id)
        )
        odj_list = result.scalars().all()

        context = {
            "request": request,
            "odj_list": odj_list,
        }
        await session.commit()

        return templates.TemplateResponse(template, context)
    await engine.dispose()


async def group_details(
    request
):
    template = "/group/details.html"

    async with async_session() as session:

        id = request.path_params["id"]

        result = await session.execute(
            select(GroupChat)
            .where(GroupChat.id==id)
        )
        detail = result.scalars().first()
        #..
        result_chat = await session.execute(
            select(MessageChat)
            .where(MessageChat.owner_group==id)
        )
        group_chat = result_chat.scalars()

        context = {
            "request": request,
            "detail": detail,
            "group_chat": group_chat,
        }
        await session.commit()

        return templates.TemplateResponse(template, context)
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def group_create(
    request
):
    template = "/group/create.html"

    async with async_session() as session:
        if request.method == "GET":
            response = templates.TemplateResponse(
                template, {"request": request,}
            )
            if not request.user.is_authenticated:
                response = RedirectResponse(
                    "/account/login",
                    status_code=302,
                )
            return response

        if request.method == "POST":
            admin_group = request.user.user_id
            form = await request.form()
            title = form["title"]
            description = form["description"]

            context = {
                "request": request,
                "title": title,
                "admin_group": admin_group,
                "description": description,
                "form": form,
            }
            response = context

            new_group = GroupChat()
            new_group.title = title
            new_group.admin_group = admin_group
            new_group.description = description

            session.add(new_group)
            session.refresh(new_group)
            await session.commit()

            response = RedirectResponse(
                f"/chat/group/{ new_group.id }",
                status_code=302,
            )
            return response

    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def group_update(
    request
):
    id = request.path_params["id"]
    template = "/group/update.html"
    admin_group = request.user.user_id

    async with async_session() as session:
        if request.method == "GET":

            result = await session.execute(
                select(GroupChat)
                .where(GroupChat.id==id)
            )
            detail = result.scalars().first()

            if detail.admin_group == admin_group:

                return templates.TemplateResponse(
                    template,
                    {
                        "request": request,
                        "detail": detail,
                    },
                )

        #...
        if request.method == "POST":

            result = await session.execute(
                select(GroupChat).where(GroupChat.id == id)
            )
            detail = result.scalars().first()

            form = await request.form()

            detail.title = form["title"]
            detail.description = form["description"]

            # ...
            file_query = (
                sqlalchemy_update(GroupChat)
                .where(GroupChat.id == id)
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
                f"/chat/group/{ detail.id }",
                status_code=302,
            )

            return response
        return templates.TemplateResponse(template, {"request": request})
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def group_delete(
    request
):
    template = "/group/delete.html"
    admin_group = request.user.user_id

    id = request.path_params["id"]

    async with async_session() as session:

        #...
        if request.method == "GET":

            result = await session.execute(
                select(GroupChat).where(GroupChat.id==id)
            )
            detail = result.scalars().first()

            if detail.admin_group == admin_group:
                return templates.TemplateResponse(
                    template,
                    {
                        "request": request,
                        "id": id,
                        "detail": detail,
                    },
                )
            return PlainTextResponse(
                "this is not your group..!"
            )

        # ...
        if request.method == "POST":

            form = await request.form()

            query = (
                delete(GroupChat).where(GroupChat.id == id)
            )
            await session.execute(query)
            await session.commit()

            context = {
                "request": request,
                "form": form,
            }

            response = templates.TemplateResponse(
                template, context
            )
            response = RedirectResponse(
                "/chat/group/list",
                status_code=302,
            )
            return response
        return templates.TemplateResponse(template, {"request": request})
    await engine.dispose()
