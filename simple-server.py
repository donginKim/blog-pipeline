#!/usr/bin/env python3
"""
간단한 FastAPI 서버
"""
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

# Database setup
DATABASE_URL = "sqlite:///./naver_monitor.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Pydantic models
class KeywordResponse(BaseModel):
    id: int
    keyword: str
    description: Optional[str]
    is_active: bool
    created_at: str
    updated_at: str

class BlogResponse(BaseModel):
    id: int
    name: str
    url_pattern: str
    description: Optional[str]
    is_active: bool
    created_at: str
    updated_at: str

class TargetResponse(BaseModel):
    id: int
    keyword_id: int
    blog_id: int
    keyword: str
    blog_name: str
    is_active: bool
    created_at: str
    updated_at: str

class DashboardStats(BaseModel):
    total_keywords: int
    total_blogs: int
    total_targets: int
    active_targets: int

# FastAPI app
app = FastAPI(title="Naver Monitor API", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Naver Monitor API v2.0", "status": "running"}

@app.get("/api/keywords", response_model=List[KeywordResponse])
async def get_keywords():
    """키워드 목록 조회"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, keyword, description, is_active, created_at, updated_at
            FROM keywords
            WHERE is_active = 1
            ORDER BY created_at DESC
        """))
        
        keywords = []
        for row in result:
            keywords.append(KeywordResponse(
                id=row[0],
                keyword=row[1],
                description=row[2],
                is_active=bool(row[3]),
                created_at=str(row[4]),
                updated_at=str(row[5])
            ))
        
        return keywords

@app.get("/api/blogs", response_model=List[BlogResponse])
async def get_blogs():
    """블로그 목록 조회"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, name, url_pattern, description, is_active, created_at, updated_at
            FROM blogs
            WHERE is_active = 1
            ORDER BY created_at DESC
        """))
        
        blogs = []
        for row in result:
            blogs.append(BlogResponse(
                id=row[0],
                name=row[1],
                url_pattern=row[2],
                description=row[3],
                is_active=bool(row[4]),
                created_at=str(row[5]),
                updated_at=str(row[6])
            ))
        
        return blogs

@app.get("/api/targets", response_model=List[TargetResponse])
async def get_targets():
    """타겟 목록 조회"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                kt.id, kt.keyword_id, kt.blog_id,
                k.keyword, b.name as blog_name,
                kt.is_active, kt.created_at, kt.updated_at
            FROM keyword_targets kt
            JOIN keywords k ON kt.keyword_id = k.id
            JOIN blogs b ON kt.blog_id = b.id
            WHERE kt.is_active = 1
            ORDER BY kt.created_at DESC
        """))
        
        targets = []
        for row in result:
            targets.append(TargetResponse(
                id=row[0],
                keyword_id=row[1],
                blog_id=row[2],
                keyword=row[3],
                blog_name=row[4],
                is_active=bool(row[5]),
                created_at=str(row[6]),
                updated_at=str(row[7])
            ))
        
        return targets

@app.get("/api/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """대시보드 통계 조회"""
    with engine.connect() as conn:
        # Total keywords
        result = conn.execute(text("SELECT COUNT(*) FROM keywords WHERE is_active = 1"))
        total_keywords = result.scalar()
        
        # Total blogs
        result = conn.execute(text("SELECT COUNT(*) FROM blogs WHERE is_active = 1"))
        total_blogs = result.scalar()
        
        # Total targets
        result = conn.execute(text("SELECT COUNT(*) FROM keyword_targets WHERE is_active = 1"))
        total_targets = result.scalar()
        
        # Active targets (same as total for now)
        active_targets = total_targets
        
        return DashboardStats(
            total_keywords=total_keywords,
            total_blogs=total_blogs,
            total_targets=total_targets,
            active_targets=active_targets
        )

if __name__ == "__main__":
    print("🚀 Naver Monitor API 서버 시작 중...")
    print("📋 접속 URL:")
    print("   - API: http://localhost:8000")
    print("   - API Docs: http://localhost:8000/docs")
    print("   - Frontend: http://localhost:3000")
    print("")
    print("🔧 테스트 계정:")
    print("   - 사용자명: testuser")
    print("   - 비밀번호: testpassword123")
    print("")
    
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)
