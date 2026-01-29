from datetime import date
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class ProfileBase(BaseModel):
    """基类"""

    name: Annotated[str, Field(..., max_length=100, description="姓名")]
    gender: Annotated[str, Field(..., max_length=20, description="性别")]
    variety: Annotated[str, Field(..., max_length=100, description="品种")]
    birthday: Annotated[date | None, Field(None, description="生日")]
    meals_per_day: Annotated[int, Field(2, ge=1, description="每日餐数")]


class ProfileCreate(ProfileBase):
    """创建宠物档案"""

    pass


class ProfileUpdate(ProfileBase):
    """更新宠物档案"""

    name: Annotated[str | None, Field(None, max_length=100, description="姓名")]
    gender: Annotated[str | None, Field(None, max_length=20, description="性别")]
    variety: Annotated[str | None, Field(None, max_length=100, description="品种")]
    birthday: date | None = None
    meals_per_day: Annotated[int | None, Field(None, ge=1, description="每日餐数")]


class ProfileResponse(ProfileBase):
    """宠物档案响应"""

    id: int
    model_config = ConfigDict(from_attributes=True)
