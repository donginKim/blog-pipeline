# Database models
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import String, Text, Boolean, DateTime, Date, ForeignKey, Integer, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..core.database import Base


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Blog(Base):
    __tablename__ = "blogs"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    url_pattern: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    keyword_targets: Mapped[List["KeywordTarget"]] = relationship(back_populates="blog", cascade="all, delete-orphan")
    results: Mapped[List["CrawlResult"]] = relationship(back_populates="blog", cascade="all, delete-orphan")


class Keyword(Base):
    __tablename__ = "keywords"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    keyword: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    keyword_targets: Mapped[List["KeywordTarget"]] = relationship(back_populates="keyword", cascade="all, delete-orphan")
    results: Mapped[List["CrawlResult"]] = relationship(back_populates="keyword", cascade="all, delete-orphan")


class KeywordTarget(Base):
    __tablename__ = "keyword_targets"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    keyword_id: Mapped[int] = mapped_column(ForeignKey("keywords.id", ondelete="CASCADE"), nullable=False)
    blog_id: Mapped[int] = mapped_column(ForeignKey("blogs.id", ondelete="CASCADE"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    keyword: Mapped["Keyword"] = relationship(back_populates="keyword_targets")
    blog: Mapped["Blog"] = relationship(back_populates="keyword_targets")
    results: Mapped[List["CrawlResult"]] = relationship(back_populates="keyword_target", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("keyword_id", "blog_id", name="uq_keyword_blog"),
        Index("ix_keyword_targets_active", "is_active"),
    )


class CrawlRun(Base):
    __tablename__ = "crawl_runs"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="running")  # running, completed, failed
    total_keywords: Mapped[int] = mapped_column(Integer, default=0)
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    fail_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    results: Mapped[List["CrawlResult"]] = relationship(back_populates="crawl_run", cascade="all, delete-orphan")


class CrawlResult(Base):
    __tablename__ = "crawl_results"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    crawl_run_id: Mapped[Optional[int]] = mapped_column(ForeignKey("crawl_runs.id", ondelete="SET NULL"), nullable=True)
    keyword_id: Mapped[int] = mapped_column(ForeignKey("keywords.id", ondelete="CASCADE"), index=True, nullable=False)
    blog_id: Mapped[int] = mapped_column(ForeignKey("blogs.id", ondelete="CASCADE"), index=True, nullable=False)
    keyword_target_id: Mapped[int] = mapped_column(ForeignKey("keyword_targets.id", ondelete="CASCADE"), nullable=False)
    
    # Crawl results
    found: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False)
    occurrences: Mapped[int] = mapped_column(Integer, default=0)
    section: Mapped[Optional[str]] = mapped_column(String(120))  # First matched section
    matched_url: Mapped[Optional[str]] = mapped_column(Text)
    matched_title: Mapped[Optional[str]] = mapped_column(Text)
    snapshot_json: Mapped[Optional[str]] = mapped_column(Text)
    
    # Metadata
    run_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)  # KST date
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    crawl_run: Mapped[Optional["CrawlRun"]] = relationship(back_populates="results")
    keyword: Mapped["Keyword"] = relationship(back_populates="results")
    blog: Mapped["Blog"] = relationship(back_populates="results")
    keyword_target: Mapped["KeywordTarget"] = relationship(back_populates="results")
    
    # Indexes
    __table_args__ = (
        Index("ix_crawl_results_daily", "run_date", "keyword_id", "blog_id"),
        Index("ix_crawl_results_found", "found", "run_date"),
    )

