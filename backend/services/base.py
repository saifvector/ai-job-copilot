import math
import uuid
from typing import Any, Dict, Generic, List, Optional, Tuple, TypeVar, Union
from pydantic import BaseModel
from core.exceptions import NotFoundException
from models.base import Base
from repositories.base import BaseRepository

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base service encapsulating core business operations and domain orchestration.
    """

    def __init__(self, repository: BaseRepository[ModelType], resource_name: str = "Resource") -> None:
        self.repository = repository
        self.resource_name = resource_name

    async def get_by_id(self, id: Union[uuid.UUID, str]) -> ModelType:
        """Fetch a model instance by ID or raise NotFoundException."""
        entity = await self.repository.get_by_id(id)
        if not entity:
            raise NotFoundException(resource=self.resource_name, identifier=str(id))
        return entity

    async def list_paginated(
        self,
        page: int = 1,
        page_size: int = 10,
        **filters: Any,
    ) -> Tuple[List[ModelType], Dict[str, Any]]:
        """Fetch paginated entities with metadata calculation."""
        page = max(1, page)
        page_size = max(1, min(100, page_size))
        skip = (page - 1) * page_size

        items = await self.repository.list(skip=skip, limit=page_size, **filters)
        total_items = await self.repository.count(**filters)
        total_pages = math.ceil(total_items / page_size) if total_items > 0 else 1

        pagination_meta = {
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        }
        return items, pagination_meta

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Create a new domain model instance."""
        return await self.repository.create(obj_in)

    async def update(self, id: Union[uuid.UUID, str], obj_in: UpdateSchemaType) -> ModelType:
        """Update an existing domain model instance or raise NotFoundException."""
        entity = await self.get_by_id(id)
        return await self.repository.update(entity, obj_in)

    async def delete(self, id: Union[uuid.UUID, str]) -> bool:
        """Delete an existing domain model instance or raise NotFoundException."""
        # Ensure existence
        await self.get_by_id(id)
        return await self.repository.delete(id)
