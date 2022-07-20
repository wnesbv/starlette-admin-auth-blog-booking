
from datetime import date, datetime, timedelta

from sqlalchemy import select, update as sqlalchemy_update, insert, delete

from starlette.authentication import requires
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.settings import settings
from db_config.storage_config import engine, async_session

from options_select.opt_slc import in_rtf, period_item
from .models import ReserveTimeFor


templates = Jinja2Templates(directory="templates")

@requires("authenticated", redirect="user_login")
# ...
async def reserve_add(
    request
):
    template = "make_an_appointment/index.html"

    async with async_session() as session:
        if request.method == "GET":
            response = templates.TemplateResponse(
                template, {"request": request,}
            )
            return response
        # ...
        if request.method == "POST":
            owner_reserve = request.user.user_id
            reserve_something = 1
            #..
            form = await request.form()
            end = form["time_end"]
            start = form["time_start"]
            #..
            time_start = datetime.strptime(
                start, settings.DATETIME
            )
            time_end = datetime.strptime(
                end, settings.DATETIME
            )
            #..
            if (
                start >= end
                or start < date.today().strftime(settings.DATE)
            ):
                return PlainTextResponse("please enter proper dates")
            #...
            generated = [
                time_start + timedelta(days=x)
                for x in range(0, (time_end - time_start).days + 1)
            ]
            reserve_period = []
            for period in generated:
                reserve_period.append(period.strftime(settings.DATETIME))
            reserve_period = str(reserve_period)
            #..
            new_rsv = ReserveTimeFor()
            new_rsv.time_end = time_end
            new_rsv.time_start = time_start
            new_rsv.owner_reserve = owner_reserve
            new_rsv.reserve_period = reserve_period
            new_rsv.reserve_something = reserve_something

            session.add(new_rsv)
            session.refresh(new_rsv)
            await session.commit()

            response = RedirectResponse(
                f"/reserve/choice/{new_rsv.id}/",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def reserve_choice(
    request
):
    template = "make_an_appointment/choice.html"
    async with async_session() as session:

        if request.method == "GET":
            #..
            rtf = await in_rtf(request, session)
            if rtf:
                #..
                obj_item = await period_item(rtf, session)
                #..
                reserve_period = rtf.reserve_period
                context = {
                    "request": request,
                    "rtf": rtf,
                    "obj_item": obj_item,
                    "reserve_period": reserve_period,
                }
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
            reserve_something = form["reserve_something"]
            #..
            time_start = rtf.time_start
            time_end = rtf.time_end
            owner_reserve = request.user.user_id
            #..
            query = (
                insert(ReserveTimeFor)
                .values(
                    reserve_something=reserve_something,
                    owner_reserve=owner_reserve,
                    time_start=time_start,
                    time_end=time_end,
                )
            )
            await session.execute(query)
            await session.commit()
            #..
            response = RedirectResponse(
                f"/item/details/{ reserve_something }",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def reserve_list(
    request
):
    template = "make_an_appointment/list.html"
    async with async_session() as session:
        #..
        stmt = await session.execute(
            select(ReserveTimeFor)
            .where(
                ReserveTimeFor.owner_reserve==request.user.user_id
            )
        )
        #..
        odj_list = stmt.scalars().all()
        if odj_list:
            context = {
                "request": request,
                "odj_list": odj_list,
            }
            return templates.TemplateResponse(
                template, context
            )
        return PlainTextResponse("This is not your account..!")
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def reserve_detail(
    request
):
    template = "make_an_appointment/details.html"
    async with async_session() as session:
        #..
        rtf = await in_rtf(request, session)
        if rtf:
            context = {
                "request": request,
                "rtf": rtf,
            }
            return templates.TemplateResponse(
                template, context
            )
        return PlainTextResponse("This is not your account..!")
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def reserve_update(
    request
):
    id = request.path_params["id"]
    template = "/make_an_appointment/update.html"

    async with async_session() as session:
        #..
        detail = await in_rtf(request, session)
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
            end = form["time_end"]
            start = form["time_start"]
            description = form["description"]
            #..
            time_end = datetime.strptime(
                end, settings.DATETIME
            )
            time_start = datetime.strptime(
                start, settings.DATETIME
            )
            #..
            if (
                start >= end
                or start < date.today().strftime(settings.DATE)
            ):
                return PlainTextResponse("please enter proper dates")
            #..
            generated = [
                time_start + timedelta(days=x)
                for x in range(0, (time_end - time_start).days + 1)
            ]
            reserve_period = detail.reserve_period
            reserve_period = []
            for period in generated:
                reserve_period.append(
                    period.strftime(settings.DATETIME)
                )
            reserve_period = str(reserve_period)
            #..
            query = (
                sqlalchemy_update(ReserveTimeFor)
                .where(ReserveTimeFor.id==id)
                .values(
                    time_end=time_end,
                    time_start=time_start,
                    description=description,
                    reserve_period=reserve_period
                )
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(query)
            await session.commit()

            response = RedirectResponse(
                f"/reserve/detail/{ detail.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def reserve_delete(
    request
):
    id = request.path_params["id"]
    template = "/make_an_appointment/delete.html"

    async with async_session() as session:

        if request.method == "GET":
            #..
            detail = await in_rtf(request, session)
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
                delete(ReserveTimeFor)
                .where(ReserveTimeFor.id == id)
            )
            await session.execute(query)
            await session.commit()
            #..
            response = RedirectResponse(
                "/reserve/list",
                status_code=302,
            )
            return response
    await engine.dispose()
