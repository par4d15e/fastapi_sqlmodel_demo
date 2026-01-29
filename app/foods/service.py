from sqlalchemy.exc import IntegrityError

from app.core.exception import AlreadyExistsException, NotFoundException
from app.foods.repository import FoodRepository
from app.foods.schema import FoodCreate, FoodResponse, FoodUpdate


class FoodService:
    """Food 服务层：封装业务逻辑并调用 repository"""

    def __init__(self, repository: FoodRepository) -> None:
        self.repository = repository

    async def get_food_by_name(self, name: str) -> FoodResponse:
        food = await self.repository.get_by_name(name)
        if not food:
            raise NotFoundException("Food not found")
        return FoodResponse.model_validate(food)

    async def get_food_by_id(self, id: int) -> FoodResponse:
        food = await self.repository.get_by_id(id)
        if not food:
            raise NotFoundException("Food not found")
        return FoodResponse.model_validate(food)

    async def list_foods(
        self,
        *,
        search: str | None = None,
        order_by: str = "id",
        direction: str = "asc",
        limit: int = 10,
        offset: int = 0,
    ) -> list[FoodResponse]:
        """查询所有食物"""
        foods = await self.repository.get_all(
            search=search,
            order_by=order_by,
            direction=direction,
            limit=limit,
            offset=offset,
        )
        return [FoodResponse.model_validate(food) for food in foods]

    async def create_food(self, food_data: FoodCreate) -> FoodResponse:
        data = food_data.model_dump()
        try:
            food = await self.repository.create(data)
            return FoodResponse.model_validate(food)
        except IntegrityError as e:
            raise AlreadyExistsException("Food with this name already exists") from e

    async def update_food(
        self,
        food_id: int,
        food_data: FoodUpdate,
    ) -> FoodResponse:
        try:
            update_data = food_data.model_dump(exclude_unset=True, exclude_none=True)
            updated = await self.repository.update(food_id, update_data)
            if not updated:
                raise NotFoundException("Food not found")
            return FoodResponse.model_validate(updated)
        except IntegrityError as e:
            raise AlreadyExistsException("Food with this name already exists") from e

    async def delete_food(self, id: int) -> bool:
        deleted = await self.repository.delete(id)
        if not deleted:
            raise NotFoundException("Food not found")
        return True
