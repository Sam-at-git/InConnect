"""
Pydantic schemas for authentication
"""

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    """Schema for login request"""

    wechat_userid: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1, max_length=100)


class LoginResponse(BaseModel):
    """Schema for login response"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    staff_id: str
    staff_name: str
    hotel_id: str
    role: str


class TokenPayload(BaseModel):
    """Schema for JWT token payload"""

    sub: str  # staff_id
    hotel_id: str
    role: str
    exp: int
