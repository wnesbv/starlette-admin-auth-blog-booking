
import enum
import sqlalchemy as sa

from sqlalchemy.orm import relationship

from db_config.storage_config import Base

from .img import FileType


class Item(Base):

    __tablename__ = "item_tm"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    title = sa.Column(sa.String, unique=True, index=True)
    description = sa.Column(sa.Text, nullable=True)
    file = sa.Column(FileType.as_mutable(sa.JSON), nullable=True)
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now())
    #..
    owner_item = sa.Column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE")
    )
    #..
    item_user = relationship(
        "User",
        back_populates="user_item",
    )
    item_cmt = relationship(
        "Comment",
        back_populates="cmt_item"
    )
    item_something = relationship(
        "ReserveTimeFor",
        back_populates="something_item",
    )
    item_service = relationship(
        "Service",
        back_populates="service_item",
    )
    item_rent = relationship(
        "Rent",
        back_populates="rent_item",
    )

    def __str__(self):
        return str(self.id)


# ...

class Service(Base):
    __tablename__ = "service_tm"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    title = sa.Column(sa.String, unique=True, index=True)
    description = sa.Column(sa.Text, nullable=True)
    file = sa.Column(FileType.as_mutable(sa.JSON), nullable=True)
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now())
    #...
    service_owner = sa.Column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE")
    )
    service_belongs = sa.Column(
        sa.Integer, sa.ForeignKey("item_tm.id", ondelete="CASCADE")
    )
    #..
    service_user = relationship(
        "User",
        back_populates="user_service",
    )
    service_item = relationship(
        "Item",
        back_populates="item_service",
    )
    service_cmt = relationship(
        "Comment",
        back_populates="cmt_service"
    )
    service_schedule = relationship(
        "Schedule",
        back_populates="schedule_service",
    )

    def __str__(self):
        return str(self.id)


class Rent(Base):
    __tablename__ = "rent_tm"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    title = sa.Column(sa.String, unique=True, index=True)
    description = sa.Column(sa.Text, nullable=True)
    file = sa.Column(FileType.as_mutable(sa.JSON), nullable=True)
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now())

    #..
    rent_owner = sa.Column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE")
    )
    rent_belongs = sa.Column(
        sa.Integer, sa.ForeignKey("item_tm.id", ondelete="CASCADE")
    )
    #..
    rent_user = relationship(
        "User",
        back_populates="user_rent",
    )
    rent_item = relationship(
        "Item",
        back_populates="item_rent",
    )
    rent_cmt = relationship(
        "Comment",
        back_populates="cmt_rent"
    )
    rent_schedule = relationship(
        "Schedule",
        back_populates="schedule_rent",
    )

    def __str__(self):
        return str(self.id)


class MyEnum(enum.Enum):
    RENT = 1
    SERVICE = 2

class Schedule(Base):
    __tablename__ = "schedule_tm"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    title = sa.Column(sa.String, unique=True, index=True)
    description = sa.Column(sa.Text, nullable=True)
    by_choose = sa.Column(sa.Enum(MyEnum), nullable=True)
    by_points = sa.Column(sa.JSON, nullable=True)
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now())
    #..
    owner_sch = sa.Column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE")
    )
    #..
    service_sch = sa.Column(
        sa.Integer, sa.ForeignKey("service_tm.id", ondelete="CASCADE")
    )
    rent_timetable = sa.Column(
        sa.Integer, sa.ForeignKey("rent_tm.id", ondelete="CASCADE")
    )
    #..
    schedule_user = relationship(
        "User",
        back_populates="user_schedule",
    )
    schedule_service = relationship(
        "Service",
        back_populates="service_schedule",
    )
    schedule_rent = relationship(
        "Rent",
        back_populates="rent_schedule",
    )

    def __str__(self):
        return str(self.id)
