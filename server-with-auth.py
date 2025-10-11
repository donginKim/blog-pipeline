#!/usr/bin/env python3
"""
로그인 기능이 포함된 FastAPI 서버
"""
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import jwt
from datetime import datetime, timedelta
import hashlib

# Database setup
DATABASE_URL = "sqlite:///./naver_monitor.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# JWT settings
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security
security = HTTPBearer()

# Pydantic models
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

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
    allow_origins=["http://localhost:3001", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    # 간단한 해시 비교 (실제로는 bcrypt 사용 권장)
    return hashed_password == hashlib.sha256(plain_password.encode()).hexdigest()

def create_access_token(data: dict):
    """JWT 토큰 생성"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """현재 사용자 정보 가져오기"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, username, email, is_active
            FROM users
            WHERE username = :username AND is_active = 1
        """), {"username": username})
        
        user = result.fetchone()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return UserResponse(
            id=user[0],
            username=user[1],
            email=user[2],
            is_active=bool(user[3])
        )

# Routes
@app.get("/")
async def root():
    return {"message": "Naver Monitor API v2.0", "status": "running"}

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """사용자 로그인"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, username, email, hashed_password, is_active
            FROM users
            WHERE username = :username AND is_active = 1
        """), {"username": login_data.username})
        
        user = result.fetchone()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # 비밀번호 검증 (간단한 해시 비교)
        stored_password = user[3]
        if not verify_password(login_data.password, stored_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # JWT 토큰 생성
        access_token = create_access_token(data={"sub": user[1]})
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user={
                "id": user[0],
                "username": user[1],
                "email": user[2],
                "is_active": bool(user[4])
            }
        )

@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    """현재 사용자 정보 조회"""
    return current_user

@app.get("/api/keywords", response_model=List[KeywordResponse])
async def get_keywords(current_user: UserResponse = Depends(get_current_user)):
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
async def get_blogs(current_user: UserResponse = Depends(get_current_user)):
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
async def get_targets(current_user: UserResponse = Depends(get_current_user)):
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
async def get_dashboard_stats(current_user: UserResponse = Depends(get_current_user)):
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
    print("   - API: http://localhost:8001")
    print("   - API Docs: http://localhost:8001/docs")
    print("   - Frontend: http://localhost:3001")
    print("")
    print("🔧 테스트 계정:")
    print("   - 사용자명: testuser")
    print("   - 비밀번호: testpassword123")
    print("")
    print("🔐 로그인 엔드포인트: POST /api/auth/login")
    print("👤 사용자 정보: GET /api/auth/me")
    print("")
    
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)

