
from sqlalchemy import select, update as sqlalchemy_update, delete

from starlette.authentication import requires
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.storage_config import engine, async_session

from mail.email import send_mail

from options_select.opt_slc import(
    user_item,
    service_comment,
    in_service,
)
from .models import Service, Schedule
from .img import FileType


templates = Jinja2Templates(directory="templates")


async def item_list(
    request
):
    template = "/item/service/list.html"

    async with async_session() as session:
        #..
        result = await session.execute(
            select(Service).order_by(Service.id)
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
    template = "/item/service/details.html"

    async with async_session() as session:
        #..
        cmt_list = await service_comment(request, session)
        #...
        result = await session.execute(
            select(Service)
            .where(Service.id==id)
        )
        detail = result.scalars().first()
        #...
        result_sch = await session.execute(
            select(Schedule)
            .join(Schedule.schedule_service)
            .where(Schedule.service_sch==id)
        )
        sch = result_sch.scalars().one_or_none()
        #...
        if not sch:
            context = {
                "request": request,
                "detail": detail,
                "cmt_list": cmt_list,
            }
        else:
            sch_json = sch.by_points
            context = {
                "request": request,
                "detail": detail,
                "cmt_list": cmt_list,
                "sch_json": sch_json,
                "sch": sch,
            }

        return templates.TemplateResponse(template, context)
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def item_create(
    request
):
    template = "/item/service/create.html"

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
            service_belongs = form["service_belongs"]
            service_owner = request.user.user_id
            #..
            file_obj = FileType.create_from(
                file=form["file"].file,
                original_filename=form["file"].filename
            )
            #..
            new_item = Service(file=file_obj)
            new_item.title = title
            new_item.description = description
            new_item.file_obj = file_obj
            new_item.service_owner = service_owner
            new_item.service_belongs = service_belongs

            session.add(new_item)
            session.refresh(new_item)
            await session.commit()

            await send_mail(
                f"A new object has been created - {new_item}: {title}"
            )

            response = RedirectResponse(
                f"/item/service/details/{ new_item.id }",
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
    template = "/item/service/update.html"

    async with async_session() as session:
        #..
        detail = await in_service(request, session)
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
                sqlalchemy_update(Service)
                .where(Service.id == id)
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
                f"/item/service/details/{ detail.id }",
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
    template = "/item/service/delete.html"

    async with async_session() as session:

        if request.method == "GET":
            #..
            detail = await in_service(request, session)
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
                delete(Service).where(Service.id == id)
            )
            await session.execute(query)
            await session.commit()
            #..
            response = RedirectResponse(
                "/item/service/list",
                status_code=302,
            )
            return response
    await engine.dispose()
