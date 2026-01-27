"""
Permission checking service and utilities
"""

from typing import List, Optional
from functools import wraps
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.permission import PermissionType, SystemRole, ROLE_PERMISSIONS
from app.models.staff import Staff
from app.dependencies import DBSession


class PermissionChecker:
    """Service for checking user permissions"""

    @staticmethod
    def get_role_permissions(role: str) -> List[PermissionType]:
        """Get permissions for a role"""
        try:
            system_role = SystemRole(role)
            return ROLE_PERMISSIONS.get(system_role, [])
        except ValueError:
            return []

    @staticmethod
    def has_permission(staff: Staff, required_permission: PermissionType) -> bool:
        """Check if staff has a specific permission"""
        # Super admin has all permissions
        if staff.role == SystemRole.SUPER_ADMIN.value:
            return True

        # Get role permissions
        role_perms = PermissionChecker.get_role_permissions(staff.role)
        return required_permission in role_perms

    @staticmethod
    def has_any_permission(staff: Staff, required_permissions: List[PermissionType]) -> bool:
        """Check if staff has any of the required permissions"""
        return any(
            PermissionChecker.has_permission(staff, perm)
            for perm in required_permissions
        )

    @staticmethod
    def can_access_hotel(staff: Staff, hotel_id: str) -> bool:
        """Check if staff can access a specific hotel"""
        # Super admin can access all hotels
        if staff.role == SystemRole.SUPER_ADMIN.value:
            return True

        # Staff can only access their own hotel
        return staff.hotel_id == hotel_id

    @staticmethod
    def can_access_department(staff: Staff, department: str | None) -> bool:
        """Check if staff can access a specific department"""
        # Super admin and hotel admin can access all departments
        if staff.role in [
            SystemRole.SUPER_ADMIN.value,
            SystemRole.HOTEL_ADMIN.value,
        ]:
            return True

        # Dept manager can access their own department
        if staff.role == SystemRole.DEPT_MANAGER.value:
            return staff.department == department

        # Regular staff can only access their own department
        return staff.department == department

    @staticmethod
    def can_modify_ticket(staff: Staff, ticket_assigned_to: str | None) -> bool:
        """Check if staff can modify a ticket"""
        # Super admin and hotel admin can modify all tickets
        if staff.role in [
            SystemRole.SUPER_ADMIN.value,
            SystemRole.HOTEL_ADMIN.value,
        ]:
            return True

        # Dept manager can modify tickets in their department
        if staff.role == SystemRole.DEPT_MANAGER.value:
            return True

        # Staff can only modify their own tickets
        return ticket_assigned_to == staff.id

    @staticmethod
    def can_view_all_tickets(staff: Staff) -> bool:
        """Check if staff can view all tickets in hotel"""
        return staff.role in [
            SystemRole.SUPER_ADMIN.value,
            SystemRole.HOTEL_ADMIN.value,
            SystemRole.DEPT_MANAGER.value,
            SystemRole.READ_ONLY.value,
        ]


# Permission dependency for FastAPI
def require_permission(permission: PermissionType):
    """Dependency factory for requiring a permission"""

    def dependency(
        staff_id: str = Depends(lambda: "current_user_id"),  # Would get from auth
        db: Session = Depends(DBSession),
    ) -> bool:
        # Get staff (simplified for MVP)
        # In real implementation, staff_id comes from JWT token
        staff = db.query(Staff).filter(Staff.id == staff_id).first()
        if not staff:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        if not PermissionChecker.has_permission(staff, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {permission.value}"
            )

        return True

    return dependency


# Decorator for checking permissions
def require_permission_decorator(permission: PermissionType):
    """Decorator for requiring a permission in route handlers"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get staff from kwargs (passed by auth middleware)
            staff = kwargs.get("current_staff")
            if not staff:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            if not PermissionChecker.has_permission(staff, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission required: {permission.value}"
                )

            return await func(*args, **kwargs)

        return wrapper
    return decorator


# Get all permissions as list
def get_all_permissions() -> List[dict]:
    """Get all available permissions"""
    return [
        {
            "name": perm.value,
            "category": perm.value.split("_")[0],
            "description": perm.value.replace("_", " ").title(),
        }
        for perm in PermissionType
    ]


# Get all roles with their permissions
def get_all_roles() -> List[dict]:
    """Get all system roles with their permissions"""
    return [
        {
            "name": role.value,
            "display_name": role.value.replace("_", " ").title(),
            "permissions": [p.value for p in perms],
        }
        for role, perms in ROLE_PERMISSIONS.items()
    ]


permission_checker = PermissionChecker()
