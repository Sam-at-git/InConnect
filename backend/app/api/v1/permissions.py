"""
Permission and Role Management API endpoints
"""

from typing import Annotated, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.schemas.common import APIResponse
from app.dependencies import DBSession
from app.core.permissions import get_all_permissions, get_all_roles, permission_checker

router = APIRouter()


@router.get("/list", response_model=APIResponse[List[dict]])
def list_permissions() -> APIResponse[List[dict]]:
    """
    Get all available permissions

    Returns:
        List of all permissions with categories
    """
    permissions = get_all_permissions()
    return APIResponse(data=permissions)


@router.get("/roles", response_model=APIResponse[List[dict]])
def list_roles() -> APIResponse[List[dict]]:
    """
    Get all system roles with their permissions

    Returns:
        List of system roles
    """
    roles = get_all_roles()
    return APIResponse(data=roles)


@router.get("/check", response_model=APIResponse[dict])
def check_permission(
    permission: str,
    role: str = "staff",
) -> APIResponse[dict]:
    """
    Check if a role has a specific permission

    Args:
        permission: Permission to check
        role: Role to check against

    Returns:
        Check result with has_permission boolean
    """
    from app.models.permission import PermissionType, SystemRole, ROLE_PERMISSIONS

    try:
        perm = PermissionType(permission)
        sys_role = SystemRole(role)
        perms = ROLE_PERMISSIONS.get(sys_role, [])
        has_perm = perm in perms

        return APIResponse(data={
            "permission": permission,
            "role": role,
            "has_permission": has_perm,
        })
    except ValueError:
        return APIResponse(data={
            "permission": permission,
            "role": role,
            "has_permission": False,
            "error": "Invalid permission or role",
        })


@router.get("/matrix", response_model=APIResponse[dict])
def get_permission_matrix() -> APIResponse[dict]:
    """
    Get permission matrix showing all roles and their permissions

    Returns:
        Matrix with roles as rows and permissions as columns
    """
    from app.models.permission import SystemRole, ROLE_PERMISSIONS

    matrix = {}

    for role, perms in ROLE_PERMISSIONS.items():
        matrix[role.value] = [p.value for p in perms]

    return APIResponse(data=matrix)


@router.get("/staff/{staff_id}", response_model=APIResponse[dict])
def get_staff_permissions(
    staff_id: str,
    db: Session = Depends(DBSession),
) -> APIResponse[dict]:
    """
    Get permissions for a specific staff member

    Args:
        staff_id: Staff ID
        db: Database session

    Returns:
        Staff permissions
    """
    from app.models.staff import Staff

    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        return APIResponse(code=404, message="Staff not found", data=None)

    perms = permission_checker.get_role_permissions(staff.role)

    return APIResponse(data={
        "staff_id": staff.id,
        "staff_name": staff.name,
        "role": staff.role,
        "department": staff.department,
        "permissions": [p.value for p in perms],
    })
