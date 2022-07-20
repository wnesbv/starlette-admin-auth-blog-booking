
from sqlalchemy import select, update as sqlalchemy_update, delete

from starlette.authentication import requires
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from json2html import json2html

from db_config.storage_config import engine, async_session

from options_select.opt_slc import item_comment, in_rent
from mail.email import send_mail

from options_select.opt_slc import in_schedule
from .models import Service, Rent, Schedule


templates = Jinja2Templates(directory="templates")


@requires("authenticated", redirect="user_login")
# ...
async def item_list(
    request
):
    template = "/item/schedule/list.html"

    async with async_session() as session:
        #..
        result = await session.execute(
            select(Schedule)
            .where(Schedule.owner_sch==request.user.user_id)
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


@requires("authenticated", redirect="user_login")
# ...
async def item_details(
    request
):
    id = request.path_params["id"]
    template = "/item/schedule/details.html"

    async with async_session() as session:

        if request.method == "GET":
            #..
            sch = await in_schedule(request, session)
            if sch:
                sch_json = sch.by_points
                table_attributes = "style='width:100%', class='table table-bordered'"
                sch_json = json2html.convert(
                    json = sch_json,
                    table_attributes=table_attributes
                )
                context = {
                    "request": request,
                    "sch_json": sch_json,
                    "sch": sch,
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
    template = "/item/schedule/create.html"

    async with async_session() as session:

        if request.method == "GET":
            #..
            stmt = await session.execute(
                select(Service)
                .where(
                    Service.service_owner == request.user.user_id
                )
            )
            odj_service = stmt.scalars().all()
            #..
            stmt = await session.execute(
                select(Rent)
                .where(
                    Rent.rent_owner == request.user.user_id
                )
            )
            odj_rent = stmt.scalars().all()

            return templates.TemplateResponse(
                template, {
                    "request": request,
                    "odj_rent": odj_rent,
                    "odj_service": odj_service,
                }
            )
        # ...
        if request.method == "POST":
            #..
            form = await request.form()
            #..
            title = form["title"]
            description = form["description"]
            #..
            by_points = form["by_points"]
            by_choose = form["by_choose"]
            #..
            service_sch = form["service_sch"]
            rent_timetable = form["rent_timetable"]
            #..
            owner_sch = request.user.user_id
            #...
            new_sch = Schedule()
            new_sch.title = title
            new_sch.description = description
            new_sch.by_choose = by_choose
            new_sch.by_points = by_points
            new_sch.owner_sch = owner_sch
            #..
            new_sch.service_sch = service_sch
            new_sch.rent_timetable = rent_timetable

            session.add(new_sch)
            session.refresh(new_sch)
            await session.commit()

            await send_mail(
                f"A new object has been created - {new_sch}: {title}"
            )

            response = RedirectResponse(
                f"/item/schedule/details/{ new_sch.id }",
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
    template = "/item/schedule/update.html"

    async with async_session() as session:
        #..
        detail = await in_schedule(request, session)
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
            form = await request.form()
            #..
            detail.title = form["title"]
            detail.description = form["description"]
            detail.by_points = form["by_points"]
            #..
            query = (
                sqlalchemy_update(Schedule)
                .where(Schedule.id == id)
                .values(form)
                .execution_options(synchronize_session="fetch")
            )

            await session.execute(query)
            await session.commit()

            await send_mail(
                f"changes were made at the facility - {detail}: {detail.title}"
            )

            response = RedirectResponse(
                f"/item/schedule/details/{ detail.id }",
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
    template = "/item/schedule/delete.html"

    async with async_session() as session:

        if request.method == "GET":
            #..
            detail = await in_schedule(request, session)
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
                delete(Schedule).where(Schedule.id == id)
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
