"""
Axorks OS — Standard API Response Helpers

Every API response follows the envelope: { data, meta, errors }
"""

from typing import Any


def success_response(
    data: Any,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Wrap a successful response in the standard envelope."""
    return {
        "data": data,
        "meta": meta,
        "errors": None,
    }


def paginated_response(
    data: list[Any],
    page: int,
    per_page: int,
    total: int,
) -> dict[str, Any]:
    """Wrap a paginated list response in the standard envelope."""
    return {
        "data": data,
        "meta": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page if per_page > 0 else 0,
        },
        "errors": None,
    }


def error_response(
    message: str,
    errors: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Wrap an error response in the standard envelope."""
    return {
        "data": None,
        "meta": None,
        "errors": errors or [{"message": message}],
    }
