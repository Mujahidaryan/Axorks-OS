"""
RBAC & Permission Tests
"""

from src.core.permissions import get_permissions_for_role, role_at_least
from src.core.tenant import TenantContext
from uuid import uuid4


def test_role_hierarchy():
    assert role_at_least("owner", "admin") is True
    assert role_at_least("admin", "manager") is True
    assert role_at_least("member", "admin") is False


def test_tenant_context_permissions():
    ctx = TenantContext(
        user_id=uuid4(),
        roles=["member"],
        permissions=get_permissions_for_role("member"),
    )

    assert ctx.has_permission("leads:read") is True
    assert ctx.has_permission("settings:manage") is False

    admin_ctx = TenantContext(
        user_id=uuid4(),
        roles=["admin"],
    )
    assert admin_ctx.has_permission("settings:manage") is True
