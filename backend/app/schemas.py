from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from datetime import datetime

# OUT
class KeywordOut(BaseModel):
    id: int
    keyword: str
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class BlogOut(BaseModel):
    id: int
    name: str
    url_pattern: str
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TargetOut(BaseModel):
    id: int
    keyword_id: int
    blog_id: int
    model_config = ConfigDict(from_attributes=True)

class BlogCredentialOut(BaseModel):
    id: int
    login_id: str
    blog_url: str
    phone: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime | None
    model_config = ConfigDict(from_attributes=True)

# IN
class AddKeywordIn(BaseModel):
    keyword: str

class UpdateKeywordIn(BaseModel):
    keyword: str | None = None
    is_active: bool | None = None

class AddBlogIn(BaseModel):
    name: str
    url_pattern: str

class UpdateBlogIn(BaseModel):
    name: str | None = None
    url_pattern: str | None = None
    is_active: bool | None = None

class AddTargetIn(BaseModel):
    keyword_id: int
    blog_id: int

class AddBlogCredentialIn(BaseModel):
    login_id: str
    password: str
    blog_url: str
    phone: str | None = None
    is_active: bool = True


class UpdateBlogCredentialIn(BaseModel):
    login_id: str | None = None
    password: str | None = None
    blog_url: str | None = None
    is_active: bool | None = None
    phone: str | None = None