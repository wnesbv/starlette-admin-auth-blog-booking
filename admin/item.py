
from sqlalchemy import select, update as sqlalchemy_update, delete, func

from starlette.authentication import requires
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.storage_config import engine, async_session

from item.models import Item, Service, Rent
from item.img import FileType
from .opt_slc import in_admin, item_comment, in_item


templates = Jinja2Templates(directory="templates")


@requires("authenticated", redirect="user_login")
# ...
async def all_list(
    request
):
    template = "/admin/index.html"
    async with async_session() as session:
        #..
        admin = await in_admin(request, session)
        #..
        if admin:
            return templates.TemplateResponse(
                template, {"request": request,}
            )
        return PlainTextResponse(
            "You are banned - this is not your account..!"
        )
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def item_list(
    request
):
    template = "/admin/list.html"
    async with async_session() as session:
        #..
        admin = await in_admin(request, session)
        #..
        if admin:
            #..
            stmt = await session.execute(
                select(Item).order_by(Item.created_at)
            )
            odj_list = stmt.scalars().all()
            #..
            stmt = await session.execute(
                select(func.count(Item.id))
            )
            odj_count = stmt.scalars().all()
            #..
            context = {
                "request": request,
                "odj_list": odj_list,
                "odj_count": odj_count,
            }
            return templates.TemplateResponse(
                template, context
            )
        return PlainTextResponse(
            "You are banned - this is not your account..!"
        )
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def item_details(
    request
):
    id = request.path_params["id"]
    template = "/admin/details.html"
    async with async_session() as session:
        #..
        admin = await in_admin(request, session)
        #..
        if admin:
            #..
            cmt_list = await item_comment(request, session)
            #..
            detail = await in_item(request, session)
            #..
            opt_service = await session.execute(
                select(Service)
                .join(Item.item_rent)
                .where(Service.service_belongs==id)
            )
            all_service = opt_service.scalars().unique()
            #..
            opt_rent = await session.execute(
                select(Rent)
                .join(Item.item_rent)
                .where(Rent.rent_belongs==id)
            )
            all_rent = opt_rent.scalars().unique()
            #..
            context = {
                "request": request,
                "detail": detail,
                "cmt_list": cmt_list,
                "all_service": all_service,
                "all_rent": all_rent,
            }
            return templates.TemplateResponse(
                template, context
            )
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def item_create(
    request
):
    template = "/admin/create.html"
    async with async_session() as session:

        if request.method == "GET":
            #..
            admin = await in_admin(request, session)
            #..
            if admin:
                return templates.TemplateResponse(
                    template, {
                        "request": request,
                    }
                )
        #...
        if request.method == "POST":
            #..
            form = await request.form()
            #..
            title = form["title"]
            description = form["description"]
            #..
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
            #..
            session.add(new_item)
            session.refresh(new_item)
            await session.commit()
            #..
            response = RedirectResponse(
                f"/admin/item/details/{ new_item.id }",
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
    template = "/admin/update.html"
    async with async_session() as session:
        #..
        admin = await in_admin(request, session)
        detail = await in_item(request, session)
        #..
        context = {
            "request": request,
            "detail": detail,
        }
        # ...
        if request.method == "GET":
            if admin:
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
            detail.title = title
            detail.description = description
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
            #..
            response = RedirectResponse(
                f"/admin/item/details/{ detail.id }",
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
    template = "/admin/delete.html"
    async with async_session() as session:

        if request.method == "GET":
            #..
            admin = await in_admin(request, session)
            detail = await in_item(request, session)
            #..
            if admin:
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
        #...
        if request.method == "POST":
            #..
            query = (
                delete(Item).where(Item.id == id)
            )
            await session.execute(query)
            await session.commit()
            #..
            response = RedirectResponse(
                "/admin/item/list",
                status_code=302,
            )
            return response
    await engine.dispose()
