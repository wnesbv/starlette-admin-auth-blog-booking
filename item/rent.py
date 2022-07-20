
from sqlalchemy import select, update as sqlalchemy_update, delete

from starlette.authentication import requires
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.storage_config import engine, async_session

from mail.email import send_mail

from options_select.opt_slc import(
    user_item,
    rent_comment,
    in_rent,
)
from .models import Rent, Schedule
from .img import FileType


templates = Jinja2Templates(directory="templates")


async def item_list(
    request
):
    template = "/item/rent/list.html"

    async with async_session() as session:
        #..
        result = await session.execute(
            select(Rent).order_by(Rent.id)
        )
        odj_list = result.scalars().all()
        #..
        context = {
            "request": request,
            "odj_list": odj_list,
        }
        return templates.TemplateResponse(
            template, context
        )
    await engine.dispose()


async def item_details(
    request
):
    template = "/item/rent/details.html"
    id = request.path_params["id"]

    async with async_session() as session:
        #..
        cmt_list = await rent_comment(request, session)
        #..
        result = await session.execute(
            select(Rent)
            .where(Rent.id==id)
        )
        detail = result.scalars().first()
        #..
        result_sch = await session.execute(
            select(Schedule)
            .join(Schedule.schedule_rent)
            .where(Schedule.rent_timetable==id)
        )
        sch_list = result_sch.scalars().all()
        #..
        context = {
            "request": request,
            "detail": detail,
            "cmt_list": cmt_list,
            "sch_list": sch_list,
        }
        return templates.TemplateResponse(template, context)
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def item_create(
    request
):
    template = "/item/rent/create.html"

    async with async_session() as session:
        if request.method == "GET":
            #..
            odj_item = await user_item(request, session)
            return templates.TemplateResponse(
                template, {
                    "request": request,
                    "odj_item": odj_item,
                }
            )
        # ...
        if request.method == "POST":
            #..
            form = await request.form()
            #..
            title = form["title"]
            description = form["description"]
            rent_belongs = form["rent_belongs"]
            rent_owner = request.user.user_id
            #..
            file_obj = FileType.create_from(
                file=form["file"].file,
                original_filename=form["file"].filename
            )
            #..
            new_item = Rent(file=file_obj)
            new_item.title = title
            new_item.description = description
            new_item.file_obj = file_obj
            new_item.rent_owner = rent_owner
            new_item.rent_belongs = rent_belongs

            session.add(new_item)
            session.refresh(new_item)
            await session.commit()

            await send_mail(
                f"A new object has been created - {new_item}: {title}"
            )

            response = RedirectResponse(
                f"/item/rent/details/{ new_item.id }",
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
    template = "/item/rent/update.html"

    async with async_session() as session:
        #..
        detail = await in_rent(request, session)
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
                sqlalchemy_update(Rent)
                .where(Rent.id == id)
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
                f"/item/rent/details/{ detail.id }",
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
    template = "/item/rent/delete.html"

    async with async_session() as session:

        if request.method == "GET":
            #..
            detail = await in_rent(request, session)
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
                delete(Rent).where(Rent.id == id)
            )
            #..
            await session.execute(query)
            await session.commit()
            #..
            response = RedirectResponse(
                "/item/rent/list",
                status_code=302,
            )
            return response
    await engine.dispose()
