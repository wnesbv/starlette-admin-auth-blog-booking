
from sqlalchemy import select, update as sqlalchemy_update, delete, func, asc, desc

from starlette.authentication import requires
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.storage_config import engine, async_session

from mail.email import send_mail

from options_select.opt_slc import item_comment, in_item
from .models import Item, Service, Rent
from .img import FileType


templates = Jinja2Templates(directory="templates")


async def item_list(
    request
):
    template = "/item/list.html"

    async with async_session() as session:
        #..
        result = await session.execute(
            select(Item).order_by(Item.created_at.desc())
        )
        odj_list = result.scalars().all()
        #..
        context = {
            "request": request,
            "odj_list": odj_list,
        }
        return templates.TemplateResponse(template, context)
    await engine.dispose()


async def item_details(
    request
):

    id = request.path_params["id"]
    template = "/item/details.html"

    async with async_session() as session:
        #..
        cmt_list = await item_comment(request, session)
        #...
        result = await session.execute(
            select(Item).where(Item.id==id)
        )
        detail = result.scalars().first()
        #...
        opt_service = await session.execute(
            select(Service)
            .join(Item.item_rent)
            .where(Service.service_belongs==id)
        )
        all_service = opt_service.scalars().unique()
        opt_rent = await session.execute(
            select(Rent)
            .join(Item.item_rent)
            .where(Rent.rent_belongs==id)
        )
        all_rent = opt_rent.scalars().unique()
        #...
        context = {
            "request": request,
            "detail": detail,
            "cmt_list": cmt_list,
            "all_service": all_service,
            "all_rent": all_rent,
        }

        await session.commit()

        return templates.TemplateResponse(template, context)
    await engine.dispose()


async def item_create(
    request
):
    template = "/item/create.html"

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
        # ...
        if request.method == "POST":
            #..
            form = await request.form()
            #..
            title = form["title"]
            description = form["description"]
            owner_item = request.user.user_id
            #..
            file_obj = FileType.create_from(
                file=form["file"].file,
                original_filename=form["file"].filename
            )
            #..
            new_item = Item(file=file_obj)
            new_item.title = title
            new_item.file_obj = file_obj
            new_item.owner_item = owner_item
            new_item.description = description

            session.add(new_item)
            session.refresh(new_item)
            await session.commit()

            await send_mail(
                f"A new object has been created - {new_item}: {title}"
            )

            response = RedirectResponse(
                f"/item/details/{ new_item.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def item_update(
    request
):
    id = request.path_params["id"]
    template = "/item/update.html"

    async with async_session() as session:
        #..
        detail = await in_item(request, session)
        #..
        context = {
            "request": request,
            "detail": detail,
        }
        # ...
        if request.method == "GET":
            if detail:
                return templates.TemplateResponse(
                    template, context
                )
            return PlainTextResponse(
                "You are banned - this is not your account..!"
            )
        # ...
        if request.method == "POST":
            #..
            form = await request.form()
            #..
            title = form["title"]
            description = form["description"]
            #..
            file_obj = FileType.create_from(
                file=form["file"].file,
                original_filename=form["file"].filename
            )
            #..
            file_query = (
                sqlalchemy_update(Item)
                .where(Item.id == id)
                .values(
                    file=file_obj,
                    title=title,
                    description=description
                )
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(file_query)
            await session.commit()

            await send_mail(
                f"changes were made at the facility - {detail}: {detail.title}"
            )

            response = RedirectResponse(
                f"/item/details/{ detail.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def item_delete(
    request
):
    id = request.path_params["id"]
    template = "/item/delete.html"

    async with async_session() as session:

        if request.method == "GET":
            #..
            detail = await in_item(request, session)
            if detail:
                return templates.TemplateResponse(
                    template,
                    {
                        "request": request,
                        "detail": detail,
                    },
                )
            return PlainTextResponse(
                "You are banned - this is not your account..!"
            )
        # ...
        if request.method == "POST":
            #..
            query = (
                delete(Item).where(Item.id == id)
            )
            await session.execute(query)
            await session.commit()
            #..
            response = RedirectResponse(
                "/item/list",
                status_code=302,
            )
            return response
    await engine.dispose()
