# app/models.py
from __future__ import annotations
from datetime import datetime, date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Boolean, DateTime, Date, ForeignKey, Integer, UniqueConstraint, Index

class Base(DeclarativeBase):
    pass

class Blog(Base):
    __tablename__ = "blogs"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    url_pattern: Mapped[str] = mapped_column(String(255), index=True)  # e.g. https://blog.naver.com/myid
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Keyword(Base):
    __tablename__ = "keywords"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    keyword: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class KeywordTarget(Base):
    __tablename__ = "keyword_targets"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    keyword_id: Mapped[int] = mapped_column(ForeignKey("keywords.id", ondelete="CASCADE"))
    blog_id: Mapped[int] = mapped_column(ForeignKey("blogs.id", ondelete="CASCADE"))
    __table_args__ = (UniqueConstraint("keyword_id", "blog_id", name="uq_keyword_blog"),)

class Run(Base):
    __tablename__ = "runs"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    total_keywords: Mapped[int] = mapped_column(Integer, default=0)
    success_cnt: Mapped[int] = mapped_column(Integer, default=0)
    fail_cnt: Mapped[int] = mapped_column(Integer, default=0)

class Result(Base):
    __tablename__ = "results"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_id: Mapped[int | None] = mapped_column(ForeignKey("runs.id", ondelete="SET NULL"), nullable=True)
    keyword_id: Mapped[int] = mapped_column(ForeignKey("keywords.id", ondelete="CASCADE"), index=True)
    blog_id: Mapped[int] = mapped_column(ForeignKey("blogs.id", ondelete="CASCADE"), index=True)
    found: Mapped[bool] = mapped_column(Boolean, index=True)
    occurrences: Mapped[int] = mapped_column(Integer, default=0)
    section: Mapped[str | None] = mapped_column(String(120))  # optional first matched section label
    matched_url: Mapped[str | None] = mapped_column(Text)
    matched_title: Mapped[str | None] = mapped_column(Text)
    snapshot_json: Mapped[str | None] = mapped_column(Text)
    run_date: Mapped[date] = mapped_column(Date, index=True)  # KST date for easy daily queries
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

Index("ix_results_daily", Result.run_date, Result.keyword_id, Result.blog_id)