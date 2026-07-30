"""
Axorks OS — Global Search Service

Full-text search across all indexed entities using PostgreSQL tsvector.
Results are grouped by entity type: leads, users, organizations, etc.
"""

from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class SearchService:
    """Full-text search service using PostgreSQL tsvector."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def search(
        self,
        query: str,
        organization_id: UUID,
        entity_types: list[str] | None = None,
        limit: int = 25,
    ) -> dict[str, list[dict]]:
        """
        Search across all indexed entities.

        Returns results grouped by entity type:
        {
            "users": [...],
            "leads": [...],
        }
        """
        if not query or not query.strip():
            return {}

        # Sanitize the search query for tsquery
        search_terms = " & ".join(
            f"{term}:*" for term in query.strip().split() if term
        )

        results: dict[str, list[dict]] = {}

        # Search users
        if not entity_types or "users" in entity_types:
            user_results = await self._search_users(
                search_terms, organization_id, limit
            )
            if user_results:
                results["users"] = user_results

        # Search leads
        if not entity_types or "leads" in entity_types:
            lead_results = await self._search_leads(
                search_terms, organization_id, limit
            )
            if lead_results:
                results["leads"] = lead_results

        return results

    async def _search_users(
        self,
        search_terms: str,
        organization_id: UUID,
        limit: int,
    ) -> list[dict]:
        """Search users within an organization."""
        sql = text("""
            SELECT u.id, u.email, u.first_name, u.last_name,
                   ts_rank(
                       to_tsvector('english',
                           coalesce(u.first_name, '') || ' ' ||
                           coalesce(u.last_name, '') || ' ' ||
                           coalesce(u.email, '')
                       ),
                       to_tsquery('english', :query)
                   ) AS rank
            FROM users u
            JOIN organization_members om ON om.user_id = u.id
            WHERE om.organization_id = :org_id
              AND u.deleted_at IS NULL
              AND to_tsvector('english',
                  coalesce(u.first_name, '') || ' ' ||
                  coalesce(u.last_name, '') || ' ' ||
                  coalesce(u.email, '')
              ) @@ to_tsquery('english', :query)
            ORDER BY rank DESC
            LIMIT :limit
        """)

        result = await self.db.execute(
            sql,
            {"query": search_terms, "org_id": str(organization_id), "limit": limit},
        )
        rows = result.fetchall()

        return [
            {
                "id": str(row.id),
                "type": "user",
                "title": f"{row.first_name or ''} {row.last_name or ''}".strip() or row.email,
                "subtitle": row.email,
                "link": f"/settings/team",
            }
            for row in rows
        ]

    async def _search_leads(
        self,
        search_terms: str,
        organization_id: UUID,
        limit: int,
    ) -> list[dict]:
        """Search leads within an organization."""
        sql = text("""
            SELECT l.id, l.business_name, l.decision_maker_name, l.email, l.status,
                   ts_rank(
                       to_tsvector('english',
                           coalesce(l.business_name, '') || ' ' ||
                           coalesce(l.decision_maker_name, '') || ' ' ||
                           coalesce(l.email, '') || ' ' ||
                           coalesce(l.notes, '')
                       ),
                       to_tsquery('english', :query)
                   ) AS rank
            FROM leads l
            WHERE l.organization_id = :org_id
              AND l.deleted_at IS NULL
              AND to_tsvector('english',
                  coalesce(l.business_name, '') || ' ' ||
                  coalesce(l.decision_maker_name, '') || ' ' ||
                  coalesce(l.email, '') || ' ' ||
                  coalesce(l.notes, '')
              ) @@ to_tsquery('english', :query)
            ORDER BY rank DESC
            LIMIT :limit
        """)

        result = await self.db.execute(
            sql,
            {"query": search_terms, "org_id": str(organization_id), "limit": limit},
        )
        rows = result.fetchall()

        return [
            {
                "id": str(row.id),
                "type": "lead",
                "title": row.business_name or row.decision_maker_name or row.email or "Untitled Lead",
                "subtitle": f"Status: {row.status} • {row.email or 'No email'}",
                "link": f"/leads/{row.id}",
            }
            for row in rows
        ]
