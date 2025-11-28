from dataclasses import dataclass
from typing import Optional, List

@dataclass
class LoginRequest:
    username: str
    password: str

@dataclass
class TokenResponse:
    access_token: str
    refresh_token: Optional[str]
    id_token: Optional[str]
    token_type: str
    expires_in: int
    scope: Optional[str]

@dataclass
class UserInfo:
    sub: str
    email: Optional[str]
    preferred_username: Optional[str]
    email_verified: Optional[bool]
    roles: List[str]
