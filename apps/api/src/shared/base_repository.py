"""
Axorks OS — Generic Base Repository

Async CRUD operations with automatic tenant scoping,
soft delete filtering, pagination, sorting, and filtering.
"""

from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.base_model import BaseModel, TenantModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """
    Generic async CRUD repository.

    Subclass and set `model` to use:
        class OrgRepository(BaseRepository[Organization]):
            model = Organization
    """

    model: type[ModelType]

    def __init__(self, db: AsyncSession):
        self.db = db

    def _base_query(self) -> Select:
        """Base query filtering out soft-deleted records."""
        return select(self.model).where(self.model.deleted_at.is_(None))  # type: ignore[union-attr]

    def _tenant_query(self, org_id: UUID) -> Select:
        """Base query scoped to a specific organization."""
        query = self._base_query()
        if issubclass(self.model, TenantModel):
            query = query.where(self.model.organization_id == org_id)  # type: ignore[attr-defined]
        return query

    async def get_by_id(self, entity_id: UUID, org_id: UUID | None = None) -> ModelType | None:
        """Get a single record by ID, optionally scoped to org."""
        query = self._base_query().where(self.model.id == entity_id)  # type: ignore[attr-defined]
        if org_id and issubclass(self.model, TenantModel):
            query = query.where(self.model.organization_id == org_id)  # type: ignore[attr-defined]
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list(
        self,
        org_id: UUID | None = None,
        page: int = 1,
        per_page: int = 25,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        filters: dict[str, Any] | None = None,
    ) -> tuple[list[ModelType], int]:
        """
        List records with pagination, sorting, and filtering.
        Returns (items, total_count).
        """
        query = self._tenant_query(org_id) if org_id else self._base_query()

        # Apply dynamic filters
        if filters:
            for field_name, value in filters.items():
                if hasattr(self.model, field_name) and value is not None:
                    column = getattr(self.model, field_name)
                    if isinstance(value, list):
                        query = query.where(column.in_(value))
                    else:
                        query = query.where(column == value)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Apply sorting
        if hasattr(self.model, sort_by):
            order_column = getattr(self.model, sort_by)
            if sort_order == "desc":
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column.asc())

        # Apply pagination
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)

        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def create(self, entity: ModelType) -> ModelType:
        """Insert a new record."""
        self.db.add(entity)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity

    async def update(self, entity: ModelType, data: dict[str, Any]) -> ModelType:
        """Update an existing record with partial data."""
        for key, value in data.items():
            if hasattr(entity, key) and value is not None:
                setattr(entity, key, value)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity

    async def soft_delete(self, entity: ModelType) -> ModelType:
        """Soft delete a record by setting deleted_at."""
        from datetime import UTC, datetime

        entity.deleted_at = datetime.now(UTC)  # type: ignore[assignment]
        await self.db.flush()
        return entity

    async def count(self, org_id: UUID | None = None) -> int:
        """Count non-deleted records, optionally scoped to org."""
        query = self._tenant_query(org_id) if org_id else self._base_query()
        count_query = select(func.count()).select_from(query.subquery())
        result = await self.db.execute(count_query)
        return result.scalar_one()
