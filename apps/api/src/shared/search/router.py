"""
Axorks OS — Global Search API

POST /api/v1/search — Full-text search across all indexed entities.
"""

from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import get_tenant_context
from src.core.response import success_response
from src.core.tenant import TenantContext
from src.shared.search.service import SearchService

router = APIRouter(prefix="/api/v1/search", tags=["Search"])


class SearchRequest(BaseModel):
    """Search request body."""
    query: str = Field(..., min_length=1, max_length=500)
    entity_types: list[str] | None = None
    limit: int = Field(default=25, ge=1, le=100)


@router.post("")
async def global_search(
    body: SearchRequest,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Search across all indexed entities.

    Results are grouped by entity type with relevance ranking.
    """
    if not ctx.org_id:
        return success_response(data={})

    service = SearchService(db)
    results = await service.search(
        query=body.query,
        organization_id=ctx.org_id,
        entity_types=body.entity_types,
        limit=body.limit,
    )
    return success_response(data=results)
