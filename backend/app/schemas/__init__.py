# Pydantic schemas for API
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# Base schemas
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# User schemas
class UserBase(BaseSchema):
    email: str = Field(..., max_length=255)
    username: str = Field(..., max_length=100)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseSchema):
    email: Optional[str] = Field(None, max_length=255)
    username: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=8)


class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime


# Blog schemas
class BlogBase(BaseSchema):
    name: str = Field(..., max_length=100)
    url_pattern: str = Field(..., max_length=255)
    description: Optional[str] = None


class BlogCreate(BlogBase):
    pass


class BlogUpdate(BaseSchema):
    name: Optional[str] = Field(None, max_length=100)
    url_pattern: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class Blog(BlogBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


# Keyword schemas
class KeywordBase(BaseSchema):
    keyword: str = Field(..., max_length=255)
    description: Optional[str] = None


class KeywordCreate(KeywordBase):
    pass


class KeywordUpdate(BaseSchema):
    keyword: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class Keyword(KeywordBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


# KeywordTarget schemas
class KeywordTargetBase(BaseSchema):
    keyword_id: int
    blog_id: int


class KeywordTargetCreate(KeywordTargetBase):
    pass


class KeywordTargetUpdate(BaseSchema):
    is_active: Optional[bool] = None


class KeywordTarget(KeywordTargetBase):
    id: int
    is_active: bool
    created_at: datetime
    keyword: Optional[Keyword] = None
    blog: Optional[Blog] = None


# CrawlRun schemas
class CrawlRunBase(BaseSchema):
    status: str = Field(default="running", max_length=50)


class CrawlRunCreate(CrawlRunBase):
    pass


class CrawlRunUpdate(BaseSchema):
    status: Optional[str] = Field(None, max_length=50)
    finished_at: Optional[datetime] = None
    total_keywords: Optional[int] = None
    success_count: Optional[int] = None
    fail_count: Optional[int] = None
    error_message: Optional[str] = None


class CrawlRun(CrawlRunBase):
    id: int
    started_at: datetime
    finished_at: Optional[datetime]
    total_keywords: int
    success_count: int
    fail_count: int
    error_message: Optional[str]


# CrawlResult schemas
class CrawlResultBase(BaseSchema):
    keyword_id: int
    blog_id: int
    keyword_target_id: int
    found: bool
    occurrences: int
    run_date: date


class CrawlResultCreate(CrawlResultBase):
    crawl_run_id: Optional[int] = None
    section: Optional[str] = Field(None, max_length=120)
    matched_url: Optional[str] = None
    matched_title: Optional[str] = None
    snapshot_json: Optional[str] = None


class CrawlResultUpdate(BaseSchema):
    found: Optional[bool] = None
    occurrences: Optional[int] = None
    section: Optional[str] = Field(None, max_length=120)
    matched_url: Optional[str] = None
    matched_title: Optional[str] = None
    snapshot_json: Optional[str] = None


class CrawlResult(CrawlResultBase):
    id: int
    crawl_run_id: Optional[int]
    section: Optional[str]
    matched_url: Optional[str]
    matched_title: Optional[str]
    snapshot_json: Optional[str]
    created_at: datetime
    keyword: Optional[Keyword] = None
    blog: Optional[Blog] = None


# Dashboard schemas
class DashboardStats(BaseSchema):
    total_keywords: int
    total_blogs: int
    total_targets: int
    total_results: int
    recent_runs: List[CrawlRun]
    recent_results: List[CrawlResult]


# Filter schemas
class ResultFilter(BaseSchema):
    keyword_id: Optional[int] = None
    blog_id: Optional[int] = None
    found: Optional[bool] = None
    run_date_from: Optional[date] = None
    run_date_to: Optional[date] = None
    limit: int = Field(default=100, le=1000)
    offset: int = Field(default=0, ge=0)

