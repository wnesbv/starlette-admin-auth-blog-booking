
from sqlalchemy import func, and_
from sqlalchemy.future import select

from starlette.templating import Jinja2Templates

from comment.models import Comment

from item.models import Item, Rent, Service, Schedule
from make_an_appointment.models import ReserveTimeFor

templates = Jinja2Templates(directory="templates")


async def in_rtf(
    request, session
):
    id = request.path_params["id"]
    stmt = await session.execute(
        select(ReserveTimeFor)
        .where(
            and_(
                ReserveTimeFor.id == id,
                ReserveTimeFor.owner_reserve == request.user.user_id,
            )
        )
    )
    result = stmt.scalars().first()
    return result


async def user_item(
    request, session
):
    stmt = await session.execute(
        select(Item)
        .where(
            Item.owner_item == request.user.user_id
        )
    )
    result = stmt.scalars().all()
    return result


async def in_item(
    request, session
):
    id = request.path_params["id"]
    stmt = await session.execute(
        select(Item)
        .where(
            and_(
                Item.id == id,
                Item.owner_item == request.user.user_id
            )
        )
    )
    result = stmt.scalars().first()
    return result


async def in_rent(
    request, session
):
    id = request.path_params["id"]
    stmt = await session.execute(
        select(Rent)
        .where(
            and_(
                Rent.id==id,
                Rent.rent_owner == request.user.user_id
            )
        )
    )
    result = stmt.scalars().first()
    return result


async def in_service(
    request, session
):
    id = request.path_params["id"]
    stmt = await session.execute(
        select(Item)
        .where(
            and_(
                Service.id == id,
                Service.service_owner == request.user.user_id
            )
        )
    )
    result = stmt.scalars().first()
    return result


async def in_schedule(
    request, session
):
    id = request.path_params["id"]
    stmt = await session.execute(
        select(Schedule)
        .where(
            and_(
                Schedule.id == id,
                Schedule.owner_sch == request.user.user_id
            )
        )
    )
    result = stmt.scalars().first()
    return result


async def period_item(
    rtf, session
):
    time_start = rtf.time_start
    time_end = rtf.time_end
    #..
    stmt = await session.execute(
        select(Item, Rent, ReserveTimeFor)
        .join(
            ReserveTimeFor.something_item,
        )
        .where(Rent.rent_belongs == Item.id)
        .where(func.date(ReserveTimeFor.time_end) < time_start)
        .where(func.date(ReserveTimeFor.time_start) < time_start)
        .where(func.date(ReserveTimeFor.time_end) < time_end)
    )
    result = stmt.scalars().unique()
    #..
    return result


async def in_comment(
    request, session
):
    stmt = await session.execute(
        select(Comment)
        .where(
            Comment.cmt_user_id == request.user.user_id
        )
    )
    result = stmt.scalars().all()
    return result


async def item_comment(
    request, session
):
    id = request.path_params["id"]
    stmt = await session.execute(
        select(Comment)
        .where(Comment.cmt_item_id == id)
        .order_by(Comment.created_at.desc())
    )
    result = stmt.scalars()
    return result


async def service_comment(
    request, session
):
    id = request.path_params["id"]
    stmt = await session.execute(
        select(Comment)
        .where(Comment.cmt_service_id == id)
        .order_by(Comment.created_at.desc())
    )
    result = stmt.scalars()
    return result


async def rent_comment(
    request, session
):
    id = request.path_params["id"]
    stmt = await session.execute(
        select(Comment)
        .where(Comment.cmt_rent_id == id)
        .order_by(Comment.created_at.desc())
    )
    result = stmt.scalars()
    return result
