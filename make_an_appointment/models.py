
import sqlalchemy as sa

from sqlalchemy.orm import relationship

from db_config.storage_config import Base


class ReserveTimeFor(Base):

    __tablename__ = "reserve_time_for"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    description = sa.Column(sa.String, nullable=True)
    reserve_time = sa.Column(sa.String, nullable=True)
    time_start = sa.Column(sa.Date, nullable=True)
    time_end = sa.Column(sa.Date, nullable=True)
    reserve_period = sa.Column(sa.String, nullable=True)
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now())
    #...
    owner_reserve = sa.Column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE")
    )
    reserve_something = sa.Column(
        sa.Integer, sa.ForeignKey("item_tm.id", ondelete="CASCADE")
    )
    #...
    reserve_user = relationship(
        "User",
        back_populates="user_reserve",
    )
    something_item = relationship(
        "Item",
        back_populates="item_something",
    )

    def __str__(self):
        return str(self.id)
