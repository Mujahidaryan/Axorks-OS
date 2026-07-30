"""
Axorks OS — SQLAlchemy Base Model

Provides the declarative base and reusable mixins for all ORM models:
- TimestampMixin: created_at, updated_at
- SoftDeleteMixin: deleted_at
- TenantMixin: organization_id
"""

import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, UUID, Boolean, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def generate_uuid() -> uuid.UUID:
    """Generate a UUID v4. (UUID v7 requires Python 3.14+ or external lib)."""
    return uuid.uuid4()


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all Axorks OS models."""
    pass


class TimestampMixin:
    """Adds created_at and updated_at columns."""

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """Adds deleted_at column for soft deletes."""

    deleted_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        default=None,
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


class TenantMixin:
    """Adds organization_id for multi-tenancy."""

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )


class BaseModel(Base, TimestampMixin, SoftDeleteMixin):
    """
    Abstract base model with:
    - UUID primary key
    - created_at, updated_at timestamps
    - deleted_at soft delete

    All Axorks OS entities inherit from this.
    """

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=generate_uuid,
    )


class TenantModel(BaseModel, TenantMixin):
    """
    Abstract base model for tenant-scoped entities.
    Includes everything from BaseModel + organization_id.
    """

    __abstract__ = True
