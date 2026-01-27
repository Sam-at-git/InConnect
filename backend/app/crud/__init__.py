"""Database CRUD operations"""

from app.crud.base import CRUDBase
from app.crud.hotel import hotel as hotel_crud
from app.crud.staff import staff as staff_crud

__all__ = ["CRUDBase", "hotel_crud", "staff_crud"]
