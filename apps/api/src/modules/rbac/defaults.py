"""
Axorks OS — Default Roles & Permissions Definition
"""

DEFAULT_ROLES: dict[str, dict] = {
    "owner": {
        "name": "owner",
        "description": "Full access to all organization resources, billing, and settings.",
        "permissions": ["*"],
    },
    "admin": {
        "name": "admin",
        "description": "Administrative access to organization and settings.",
        "permissions": ["*"],
    },
    "manager": {
        "name": "manager",
        "description": "Manage leads, projects, team assignments, and view reports.",
        "permissions": [
            "leads:*",
            "crm:*",
            "projects:*",
            "proposals:*",
            "finance:read",
            "knowledge:*",
            "analytics:read",
            "settings:read",
            "users:read",
        ],
    },
    "member": {
        "name": "member",
        "description": "Standard team member with write access to projects, CRM, and leads.",
        "permissions": [
            "leads:read", "leads:write",
            "crm:read", "crm:write",
            "projects:read", "projects:write",
            "proposals:read", "proposals:write",
            "knowledge:read", "knowledge:write",
            "analytics:read",
        ],
    },
    "viewer": {
        "name": "viewer",
        "description": "Read-only access across standard business modules.",
        "permissions": [
            "leads:read",
            "crm:read",
            "projects:read",
            "proposals:read",
            "knowledge:read",
            "analytics:read",
        ],
    },
}
