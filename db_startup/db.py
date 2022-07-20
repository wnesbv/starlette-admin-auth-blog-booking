
import datetime

from passlib.hash import pbkdf2_sha1

from item.models import Item, Service, Schedule, Rent
from comment.models import Comment
from account.models import User
from participant.models import PersonParticipant
from channel.models import GroupChat, MessageChat
from make_an_appointment.models import ReserveTimeFor


from db_config.storage_config import Base, engine, async_session


async def on_app_startup() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        async with session.begin():

            password_hash = pbkdf2_sha1.hash("password")
            session.add_all(
                [
                    User(
                        id=1,
                        name="User One",
                        email="one@example.com",
                        username="user-one",
                        password=password_hash,
                        is_admin=True,
                        is_active=True,
                        email_verified=True,
                    ),
                    User(
                        id=2,
                        name="user two",
                        email="two@example.com",
                        username="two-user",
                        password=password_hash,
                        is_admin=False,
                        is_active=True,
                        email_verified=True,
                    ),
                    Comment(
                        id=1,
                        opinion="01 (one) item-opinion description",
                        cmt_user_id=1,
                        cmt_item_id=1,
                    ),
                    Comment(
                        id=2,
                        opinion="01 (one) service-opinion description",
                        cmt_user_id=1,
                        cmt_service_id=1,
                    ),
                    GroupChat(
                        title="group one",
                        description="description group",
                        admin_group=1,
                    ),
                    MessageChat(
                        message="message",
                        owner_chat=1,
                        owner_group=1,
                    ),
                    PersonParticipant(
                        explanations_person="one@example.com - explanations_person",
                        permission=0,
                        participant=2,
                        group_participant=1,
                    ),
                    ReserveTimeFor(
                        time_start=datetime.date.today(),
                        time_end=datetime.date.today() + datetime.timedelta(days=1),
                        owner_reserve=1,
                        reserve_something=1,
                    ),
                    Item(
                        id=1,
                        title="item 01 one",
                        description="description",
                        owner_item=1,
                    ),
                    Item(
                        id=2,
                        title="item 02 two",
                        description="description 02 two",
                        owner_item=2,
                    ),
                    Service(
                        title="service 01",
                        description="description 01",
                        service_owner=1,
                        service_belongs=1,
                    ),
                    Schedule(
                        id=1,
                        title="schedule 01",
                        by_choose="RENT",
                        owner_sch=1,
                        rent_timetable=1,
                        by_points="[{\"title\":\"event01\",\"start\":\"2022-06-20T00:00:00\",\"end\":\"2022-06-25T24:00:00\"},{\"title\":\"event02\",\"start\":\"2022-06-26T00:00:00\",\"end\":\"2022-06-30T24:00:00\"}]"
                        ),
                    Schedule(
                        id=2,
                        title="schedule 02",
                        by_choose="SERVICE",
                        owner_sch=2,
                        service_sch=1,
                        by_points="[{\"date\":\"June/1/2022\",\"description\":\"Author note: Thank you for using EvoCalendar!\",\"everyYear\":\"!0\",\"id\":\"1\",\"name\":\"Author Two\",\"type\":\"birthday\"},{\"date\":\"June/2/2022\",\"description\":\"Author's note: Thank you for using EvoCalendar!\",\"everyYear\":\"!0\",\"id\":\"2\",\"name\":\"Author Two\",\"type\":\"birthday\"},{\"date\":\"June/11/2022\",\"description\":\"Lorem ipsum dolor sit amet!\",\"everyYear\":\"!0\",\"id\":\"3\",\"name\":\"Author Two\",\"type\":\"birthday\"}]"
                        ),
                    Rent(
                        title="rent 01",
                        rent_owner=1,
                        rent_belongs=1,
                    ),
                    Rent(
                        title="rent 02",
                        rent_owner=2,
                        rent_belongs=2,
                    ),
                ]
            )
            await session.flush()
        await session.commit()
    await engine.dispose()


async def on_app_shutdown() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
