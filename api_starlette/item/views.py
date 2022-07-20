#import json

from sqlalchemy import update as sqlalchemy_update, delete
from sqlalchemy.future import select

from starlette.requests import Request
from starlette.templating import Jinja2Templates
from starlette.responses import (
    Response,
    JSONResponse,
    RedirectResponse,
    PlainTextResponse,
)

from item.models import Item
from item.img import FileType

from db_config.storage_config import engine, async_session

from mail.email import send_mail


templates = Jinja2Templates(directory="templates")


async def item_list(
    request
):
    async with async_session() as session:

        result = await session.execute(select(Item))
        obj_list = result.scalars().all()
        await session.commit()

        obj = [
            {
                "id": to.id,
                "title": to.title,
                "description": to.description,
                "file": to.file,
            }
            for to in obj_list
        ]
        return JSONResponse(obj)

        # return Response(
        #     json.dumps(obj, default=str),
        # )

    await engine.dispose()


async def item_details(
    request
):

    async with async_session() as session:

        id = request.path_params["id"]

        result = await session.execute(
            select(Item).where(Item.id == id)
        )
        obj_list = result.scalars()
        await session.commit()

        obj = [
            {
                "id": to.id,
                "title": to.title,
                "description": to.description,
                "file": to.file,
            }
            for to in obj_list
        ]
        return JSONResponse(obj)

    await engine.dispose()


async def item_create(request):

    template = "/item/create.html"

    async with async_session() as session:
        if request.method == "GET":
            response = templates.TemplateResponse(
                template, {"request": request}
            )
            if not request.user.is_authenticated:
                response = RedirectResponse(
                    "/account/login",
                    status_code=302,
                )
            return response

        if request.method == "POST":
            form = await request.form()
            title = form["title"]
            description = form["description"]
            owner_item = request.user.user_id

            context = {
                "request": request,
                "title": title,
                "description": description,
                "owner_item": owner_item,
                "form": form,
            }
            response = context

            # ...
            file_obj = FileType.create_from(
                file=form["file"].file, original_filename=form["file"].filename
            )
            # ...

            new_item = Item(file=file_obj)
            new_item.title = title
            new_item.file_obj = file_obj
            new_item.owner_item = owner_item
            new_item.description = description

            session.add(new_item)
            session.refresh(new_item)
            await session.commit()

            await send_mail(f"A new object has been created - {new_item}: {title}")

            response = RedirectResponse(
                f"/item/details/{ new_item.id }",
                status_code=302,
            )
            return response

    await engine.dispose()


# ...


async def item_update(request):
    template = "/item/update.html"
    owner_item = request.user.user_id
    id = request.path_params["id"]

    async with async_session() as session:
        # ...
        if request.method == "GET":

            result = await session.execute(select(Item).where(Item.id == id))
            detail = result.scalars().first()

            if detail.owner_item == owner_item:

                return templates.TemplateResponse(
                    template,
                    {
                        "request": request,
                        "id": id,
                        "detail": detail,
                    },
                )

        # ...
        if request.method == "POST":

            result = await session.execute(select(Item).where(Item.id == id))
            detail = result.scalars().first()

            form = await request.form()

            detail.title = form["title"]
            detail.description = form["description"]

            # ...
            file_obj = FileType.create_from(
                file=form["file"].file, original_filename=form["file"].filename
            )
            file_query = (
                sqlalchemy_update(Item)
                .where(Item.id == id)
                .values(file=file_obj)
                .execution_options(synchronize_session="fetch")
            )

            await session.execute(file_query)
            await session.commit()

            context = {
                "request": request,
                "detail": detail,
            }

            await send_mail(
                f"changes were made at the facility - {detail}: {detail.title}"
            )

            response = templates.TemplateResponse(template, context)
            response = RedirectResponse(
                f"/item/details/{ detail.id }",
                status_code=302,
            )

            return response
        return templates.TemplateResponse(template, {"request": request})

    await engine.dispose()


async def item_delete(request):
    template = "/item/delete.html"
    owner_item = request.user.user_id
    id = request.path_params["id"]

    async with async_session() as session:
        # ...
        if request.method == "GET":

            result = await session.execute(select(Item).where(Item.id == id))
            detail = result.scalars().first()

            if detail.owner_item == owner_item:
                return templates.TemplateResponse(
                    template,
                    {
                        "request": request,
                        "id": id,
                        "detail": detail,
                    },
                )
            return PlainTextResponse("You are banned - this is not your account..!")
        # ...
        if request.method == "POST":

            form = await request.form()

            query = delete(Item).where(Item.id == id)
            await session.execute(query)
            await session.commit()

            context = {
                "request": request,
                "form": form,
            }

            response = templates.TemplateResponse(template, context)
            response = RedirectResponse(
                "/item/list",
                status_code=302,
            )

            return response
        return templates.TemplateResponse(template, {"request": request})

    await engine.dispose()
