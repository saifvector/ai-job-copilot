import uuid
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Generic asynchronous base repository providing standard CRUD operations.
    Follows repository pattern for database abstraction and testability.
    """

    def __init__(self, model: Type[ModelType], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def get_by_id(self, id: Union[uuid.UUID, str]) -> Optional[ModelType]:
        """Fetch a single record by its primary key UUID."""
        if isinstance(id, str):
            id = uuid.UUID(id)
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    get = get_by_id

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters: Any,
    ) -> List[ModelType]:
        """Fetch a paginated list of records with optional field equality filtering."""
        stmt = select(self.model)
        for attr, val in filters.items():
            if hasattr(self.model, attr) and val is not None:
                stmt = stmt.where(getattr(self.model, attr) == val)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(self, **filters: Any) -> int:
        """Count total matching records."""
        stmt = select(func.count()).select_from(self.model)
        for attr, val in filters.items():
            if hasattr(self.model, attr) and val is not None:
                stmt = stmt.where(getattr(self.model, attr) == val)
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def create(self, obj_in: Union[BaseModel, Dict[str, Any], ModelType]) -> ModelType:
        """Create a new model instance from Pydantic schema, dictionary, or model instance."""
        if isinstance(obj_in, self.model):
            self.session.add(obj_in)
            await self.session.flush()
            await self.session.refresh(obj_in)
            return obj_in
        elif isinstance(obj_in, BaseModel):
            values = obj_in.model_dump(exclude_unset=True)
        else:
            values = obj_in.copy()
        db_obj = self.model(**values)
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db_obj: ModelType,
        obj_in: Union[BaseModel, Dict[str, Any]],
    ) -> ModelType:
        """Update an existing model instance."""
        if isinstance(obj_in, BaseModel):
            update_data = obj_in.model_dump(exclude_unset=True)
        else:
            update_data = obj_in.copy()

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, id: Union[uuid.UUID, str]) -> bool:
        """Delete a record by primary key UUID."""
        db_obj = await self.get_by_id(id)
        if db_obj:
            await self.session.delete(db_obj)
            await self.session.flush()
            return True
        return False
