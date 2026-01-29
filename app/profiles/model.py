from datetime import date

from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base_model import Base, DateTimeMixin
from app.reminders.model import Reminder


class Profile(Base, DateTimeMixin):
    __tablename__ = "profiles"
    __table_args__ = {"comment": "档案表"}

    id: Mapped[int | None] = mapped_column(Integer, primary_key=True, comment="宠物ID")
    name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, comment="姓名"
    )
    gender: Mapped[str] = mapped_column(String(20), nullable=False, comment="性别")
    variety: Mapped[str] = mapped_column(String(100), nullable=False, comment="品种")
    birthday: Mapped[date | None] = mapped_column(Date, nullable=True, comment="生日")
    meals_per_day: Mapped[int] = mapped_column(
        Integer, nullable=False, default=2, comment="每日餐数"
    )
    description: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="描述"
    )
    reminders: Mapped[list["Reminder"]] = relationship(
        back_populates="profile", comment="提醒事项列表"
    )
