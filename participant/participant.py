
from sqlalchemy import delete

from sqlalchemy import select, func, and_

from starlette.authentication import requires
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from account.models import User

from db_config.storage_config import engine, async_session

from channel.models import GroupChat
from .models import PersonParticipant


templates = Jinja2Templates(directory="templates")


@requires("authenticated", redirect="user_login")
# ...
async def participant_create(
    request
):
    id = request.path_params["id"]
    template = "/participant/create.html"

    async with async_session() as session:

        if request.method == "GET":
            #..
            stmt = await session.execute(
                select(PersonParticipant)
                .where(
                    PersonParticipant.group_participant == id,
                    PersonParticipant.participant == request.user.user_id
                )
            )
            #..
            double = stmt.scalars().all()
            if not double:
                return templates.TemplateResponse(
                    template, {"request": request,}
                )
            return RedirectResponse(
                f"/chat/group/{id}",
                status_code=302,
            )
        # ...
        if request.method == "POST":
            #..
            group_participant = id
            participant = request.user.user_id
            #..
            form = await request.form()
            explanations_person = form["explanations_person"]
            #..
            context = {
                "request": request,
                "participant": participant,
                "group_participant": group_participant,
                "explanations_person": explanations_person,
                "form": form,
            }
            response = context

            new_participant = PersonParticipant()
            new_participant.participant = participant
            new_participant.group_participant = group_participant
            new_participant.explanations_person = explanations_person

            session.add(new_participant)
            session.refresh(new_participant)
            await session.commit()

            response = RedirectResponse(
                f"/chat/group/{id}",
                status_code=302,
            )
            return response

    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def participant_list(
    request
):
    id = request.path_params["id"]
    template = "/participant/list.html"

    async with async_session() as session:
        #..
        stmt = await session.execute(
            select(PersonParticipant)
            .join(GroupChat)
            .where(
                PersonParticipant.group_participant == id,
                GroupChat.admin_group == request.user.user_id
            )
        )
        #..
        odj_admin = stmt.scalars().first()
        if odj_admin:
            stmt = await session.execute(
                select(PersonParticipant)
                .where(
                    PersonParticipant.group_participant == id
                )
            )
            odj_list = stmt.scalars().all()
            context = {
                "request": request,
                "odj_list": odj_list,
            }
            return templates.TemplateResponse(
                template, context
            )
        return PlainTextResponse("Or, you don't have viewing rights. Or, there are no applications")
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def participant_add(
    request
):
    id = request.path_params["id"]

    async with async_session() as session:
        #..
        stmt = await session.execute(
            select(PersonParticipant)
            .join(GroupChat)
            .where(
                PersonParticipant.group_participant == id,
                GroupChat.admin_group == request.user.user_id
            )
        )
        odj_admin = stmt.scalars().first()

        if odj_admin:
            stmt = await session.execute(
                select(PersonParticipant)
                .where(
                    PersonParticipant.id == id,
                )
            )
            detail = stmt.scalars().first()

            detail.permission = True
            await session.commit()

            context = {
                "request": request,
            }
            response = context
            response = RedirectResponse(
                "/chat/group/list",
                status_code=302,
            )
            return response

    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def participant_delete(
    request
):
    id = request.path_params["id"]

    async with async_session() as session:
        #..
        stmt = await session.execute(
            select(PersonParticipant)
            .join(GroupChat)
            .where(
                PersonParticipant.group_participant == id,
                GroupChat.admin_group == request.user.user_id
            )
        )
        odj_admin = stmt.scalars().first()

        if odj_admin:
            query = (
                delete(PersonParticipant).where(
                    PersonParticipant.id == id
                )
            )
            await session.execute(query)
            await session.commit()

            context = {
                "request": request,
            }
            response = context
            response = RedirectResponse(
                "/chat/group/list",
                status_code=302,
            )
            return response

    await engine.dispose()
