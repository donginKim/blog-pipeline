#!/usr/bin/env python3
"""
디버깅 로그가 추가된 FastAPI 서버
"""
import sys
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn
import jwt
from datetime import datetime, timedelta
import hashlib
import pandas as pd
import io
import asyncio
from playwright.async_api import async_playwright
import random
import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# AI 블로그 작성 기능
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAI 패키지가 설치되지 않았습니다. AI 블로그 작성 기능이 비활성화됩니다.")
    print("   설치 방법: pip install openai")

# Database setup
# 환경 변수에서 DATABASE_URL 가져오기 (Docker에서 사용)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{os.path.join(os.path.dirname(__file__), 'naver_monitor.db')}"
)
print(f"🔍 데이터베이스 경로: {DATABASE_URL}")

# PostgreSQL의 경우 connect_args 제거
if DATABASE_URL.startswith("postgresql"):
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
else:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Security
security = HTTPBearer()

# 설정 관련 함수 (데이터베이스 저장)
import json

def get_notification_settings():
    """알림 설정 가져오기 (DB에서)"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT value FROM settings WHERE key = 'notification_settings'"))
            row = result.fetchone()
            if row:
                return json.loads(row[0])
            return None
    except Exception as e:
        print(f"❌ 알림 설정 조회 오류: {e}")
        return None

def save_notification_settings(settings: dict):
    """알림 설정 저장 (DB에)"""
    try:
        with engine.connect() as conn:
            settings_json = json.dumps(settings)
            conn.execute(text("""
                INSERT OR REPLACE INTO settings (key, value, updated_at) 
                VALUES ('notification_settings', :value, CURRENT_TIMESTAMP)
            """), {"value": settings_json})
            conn.commit()
            print(f"✅ 알림 설정 저장 완료: {settings}")
            return True
    except Exception as e:
        print(f"❌ 알림 설정 저장 오류: {e}")
        return False

def get_schedule_settings():
    """스케줄 설정 가져오기 (DB에서)"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT value FROM settings WHERE key = 'schedule_settings'"))
            row = result.fetchone()
            if row:
                return json.loads(row[0])
            return None
    except Exception as e:
        print(f"❌ 스케줄 설정 조회 오류: {e}")
        return None

def save_schedule_settings(settings: dict):
    """스케줄 설정 저장 (DB에)"""
    try:
        with engine.connect() as conn:
            settings_json = json.dumps(settings)
            conn.execute(text("""
                INSERT OR REPLACE INTO settings (key, value, updated_at) 
                VALUES ('schedule_settings', :value, CURRENT_TIMESTAMP)
            """), {"value": settings_json})
            conn.commit()
            print(f"✅ 스케줄 설정 저장 완료: {settings}")
            return True
    except Exception as e:
        print(f"❌ 스케줄 설정 저장 오류: {e}")
        return False

def get_ai_blog_settings():
    """AI 블로그 설정 가져오기 (DB에서)"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT value FROM settings WHERE key = 'ai_blog_settings'"))
            row = result.fetchone()
            if row:
                return json.loads(row[0])
            # 기본값 반환
            return {"enabled": False, "use_openai": False}
    except Exception as e:
        print(f"❌ AI 블로그 설정 조회 오류: {e}")
        return {"enabled": False, "use_openai": False}

def save_ai_blog_settings(settings: dict):
    """AI 블로그 설정 저장 (DB에)"""
    try:
        with engine.connect() as conn:
            settings_json = json.dumps(settings)
            conn.execute(text("""
                INSERT OR REPLACE INTO settings (key, value, updated_at) 
                VALUES ('ai_blog_settings', :value, CURRENT_TIMESTAMP)
            """), {"value": settings_json})
            conn.commit()
            print(f"✅ AI 블로그 설정 저장 완료: {settings}")
            return True
    except Exception as e:
        print(f"❌ AI 블로그 설정 저장 오류: {e}")
        return False

# 알리고 SMS 설정 (환경변수에서 가져오기)
ALIGO_API_KEY = os.getenv("ALIGO_API_KEY", "")
ALIGO_USER_ID = os.getenv("ALIGO_USER_ID", "")
ALIGO_SENDER = os.getenv("ALIGO_SENDER", "")

# SMS 발송 함수 (알리고 SMS API)
async def send_sms_notification(phone_number: str, message: str):
    """알리고 SMS 알림 발송"""
    try:
        print(f"📱 SMS 발송 시도: {phone_number}")
        print(f"📝 메시지: {message}")
        
        # API 키가 설정되지 않은 경우 테스트 모드
        if not ALIGO_API_KEY or not ALIGO_USER_ID or not ALIGO_SENDER:
            print("⚠️ 알리고 API 설정이 없습니다. 테스트 모드로 실행합니다.")
            print(f"   설정 방법: .env 파일에 ALIGO_API_KEY, ALIGO_USER_ID, ALIGO_SENDER 추가")
            return True
        
        # 전화번호 포맷팅 (하이픈 제거)
        formatted_phone = phone_number.replace("-", "").replace(" ", "")
        
        # 알리고 SMS API 호출
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://apis.aligo.in/send/",
                data={
                    "key": ALIGO_API_KEY,
                    "userid": ALIGO_USER_ID,
                    "sender": ALIGO_SENDER,
                    "receiver": formatted_phone,
                    "msg": message,
                    "msg_type": "SMS",  # SMS, LMS, MMS
                    "title": "Naver Monitor",  # LMS/MMS 제목
                }
            )
            
            result = response.json()
            print(f"📱 알리고 응답: {result}")
            
            if result.get('result_code') == '1':
                print(f"✅ SMS 발송 성공: {formatted_phone}")
                return True
            else:
                print(f"❌ SMS 발송 실패: {result.get('message', 'Unknown error')}")
                return False
                
    except Exception as e:
        print(f"❌ SMS 발송 중 오류: {e}")
        return False

# Crawling functions
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
)

async def parse_naver_search_page(page):
    """네이버 검색 결과 페이지 파싱 - 연관 검색어 포함"""
    results = []

    # 일반 섹션
    container_divs = await page.query_selector_all(
        "div.sds-comps-base-layout.sds-comps-inline-layout.fds-collection-root"
    )

    for div in container_divs:
        span = await div.query_selector("span")
        if not span:
            continue

        span_text = (await span.inner_text() or "").strip()
        if not span_text or "인기주제" in span_text:
            continue
        
        # span_text가 연관 검색어 (예: "파이썬게임", "파이썬 자동화")
        print(f"🔍 섹션 발견: {span_text}")

        boxes = await div.query_selector_all(
            "div.sds-comps-base-layout.sds-comps-inline-layout._keep_wrap.fds-article-simple-box.fds-article-box-mobilefalse"
        )

        article_boxes = []
        for idx, box in enumerate(boxes, start=1):
            seen_links = set()
            links = []

            a_elements = await box.query_selector_all("a")
            for a in a_elements:
                href = (await a.get_attribute("href") or "").strip()
                text = (await a.inner_text() or "").strip()
                key = (href, text)

                if (
                        href.startswith("https://blog.naver.com")
                        and text
                        and key not in seen_links
                ):
                    seen_links.add(key)
                    links.append({"href": href, "text": text})

            if links:
                article_boxes.append({"box_index": idx, "links": links})

        if article_boxes:
            results.append({"span": span_text, "article_boxes": article_boxes})

    # 인기글 섹션
    subject_divs = await page.query_selector_all("div.api_subject_bx")

    for div in subject_divs:
        title_elem = await div.query_selector("div.mod_title_area .title_wrap h2.title")
        if not title_elem:
            continue

        title_text = (await title_elem.inner_text() or "").strip()
        if "인기글" not in title_text:
            continue

        user_boxes = await div.query_selector_all("ul.lst_view div.user_box_inner")
        article_boxes = []

        for idx, user_box in enumerate(user_boxes, start=1):
            a = await user_box.query_selector("div.user_info a")
            if not a:
                continue

            href = (await a.get_attribute("href") or "").strip()
            text = (await a.inner_text() or "").strip()

            if href.startswith("https://blog.naver.com") and text:
                article_boxes.append({
                    "box_index": idx,
                    "links": [{"href": href, "text": text}],
                })

        if article_boxes:
            results.append({"span": title_text, "article_boxes": article_boxes})

    return results

async def crawl_keyword_async(keyword: str, timeout_ms: int = 120000, max_retries: int = 3):
    """키워드 크롤링 (비동기) - 재시도 로직 포함"""
    for attempt in range(max_retries):
        try:
            print(f"🔍 크롤링 시도 {attempt + 1}/{max_retries}: {keyword}")
            
            async with async_playwright() as p:
                # 시스템 chromium 사용 (Docker 경량화)
                chromium_path = os.getenv('CHROMIUM_PATH', None)
                launch_options = {
                    'headless': True,
                    'args': [
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-accelerated-2d-canvas',
                        '--no-first-run',
                        '--no-zygote',
                        '--disable-gpu'
                    ]
                }
                
                # Docker 환경에서 시스템 chromium 사용
                if chromium_path:
                    launch_options['executable_path'] = chromium_path
                
                browser = await p.chromium.launch(**launch_options)
                
                # 페이지 설정
                page = await browser.new_page()
                await page.set_extra_http_headers({
                    "User-Agent": USER_AGENT,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1"
                })
                
                # 네트워크 타임아웃 설정
                page.set_default_timeout(timeout_ms)
                page.set_default_navigation_timeout(timeout_ms)
                
                # URL 인코딩
                import urllib.parse
                encoded_keyword = urllib.parse.quote(keyword)
                url = f"https://search.naver.com/search.naver?query={encoded_keyword}"
                
                print(f"🔍 네이버 검색 페이지 접속: {url}")
                
                # 페이지 로딩 (재시도 로직)
                try:
                    await page.goto(url, wait_until='domcontentloaded', timeout=timeout_ms)
                except Exception as e:
                    print(f"⚠️ 페이지 로딩 실패 (시도 {attempt + 1}): {e}")
                    if attempt < max_retries - 1:
                        await browser.close()
                        await asyncio.sleep(2 ** attempt)  # 지수 백오프
                        continue
                    else:
                        raise
                
                # 추가 대기 시간
                wait_time = 5000 + random.randint(0, 3000)
                print(f"🔍 페이지 로딩 완료, {wait_time}ms 대기 중...")
                await page.wait_for_timeout(wait_time)
                
                # 페이지 로딩 확인
                try:
                    await page.wait_for_selector('body', timeout=10000)
                except Exception as e:
                    print(f"⚠️ 페이지 본문 로딩 실패: {e}")
                    if attempt < max_retries - 1:
                        await browser.close()
                        await asyncio.sleep(2 ** attempt)
                        continue
                    else:
                        raise
                
                # 결과 파싱
                print(f"🔍 검색 결과 파싱 시작: {keyword}")
                results = await parse_naver_search_page(page)
                print(f"✅ 파싱 완료: {len(results)}개 섹션 발견")
                
                await browser.close()
                return results
                
        except Exception as e:
            print(f"❌ 크롤링 실패 (시도 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # 지수 백오프
                continue
            else:
                raise e
    
    return []

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

class RecentActivity(BaseModel):
    id: int
    keyword: str
    blog_name: str
    status: str
    created_at: str

class CrawlRequest(BaseModel):
    keyword_id: Optional[int] = None
    blog_id: Optional[int] = None
    target_id: Optional[int] = None

class CrawlResult(BaseModel):
    id: int
    crawl_run_id: int
    keyword: str
    blog_name: str
    rank: int
    title: str
    url: str
    snippet: str
    section: Optional[str]
    created_at: str

class CrawlRun(BaseModel):
    id: int
    keyword: str
    blog_name: str
    status: str
    started_at: Optional[str]
    completed_at: Optional[str]
    error_message: Optional[str]
    created_at: str

class GeneratedPost(BaseModel):
    id: int
    keyword_id: int
    crawl_run_id: int
    title: str
    content: str
    summary: Optional[str]
    tags: Optional[str]
    status: str
    created_at: str
    published_at: Optional[str]

class BlogCreate(BaseModel):
    name: str
    url_pattern: str
    description: Optional[str] = None

class BlogUpdate(BaseModel):
    name: Optional[str] = None
    url_pattern: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class BlogResponse(BaseModel):
    id: int
    name: str
    url_pattern: str
    description: Optional[str]
    is_active: bool
    created_at: str
    updated_at: str

class KeywordCreate(BaseModel):
    keyword: str
    description: Optional[str] = None

class KeywordUpdate(BaseModel):
    keyword: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class KeywordResponse(BaseModel):
    id: int
    keyword: str
    description: Optional[str]
    is_active: bool
    created_at: str
    updated_at: str

# FastAPI app
app = FastAPI(title="Naver Monitor API", version="2.0.0")

# 스케줄러 초기화
scheduler = AsyncIOScheduler()

async def scheduled_crawl_job():
    """스케줄된 크롤링 작업"""
    print("⏰ 스케줄된 크롤링 시작!")
    
    try:
        with engine.connect() as conn:
            # 모든 활성 타겟 조회
            result = conn.execute(text("""
                SELECT kt.id, k.keyword, b.name as blog_name, k.id as keyword_id, b.id as blog_id
                FROM keyword_targets kt
                JOIN keywords k ON kt.keyword_id = k.id
                JOIN blogs b ON kt.blog_id = b.id
                WHERE kt.is_active = 1
                LIMIT 10
            """))
            
            targets = result.fetchall()
            print(f"📊 스케줄 크롤링: {len(targets)}개 타겟")
            
            # 각 타겟 크롤링
            for target in targets:
                target_id, keyword, blog_name, k_id, b_id = target
                
                # 크롤링 실행 기록 생성
                result = conn.execute(text("""
                    INSERT INTO crawl_runs (keyword_id, blog_id, status, started_at)
                    VALUES (:keyword_id, :blog_id, 'running', CURRENT_TIMESTAMP)
                """), {"keyword_id": k_id, "blog_id": b_id})
                
                run_id = result.lastrowid
                conn.commit()
                
                # 크롤링 실행
                await run_crawl_task(run_id, keyword, blog_name, k_id, b_id)
            
            print(f"✅ 스케줄 크롤링 완료: {len(targets)}개 타겟")
            
    except Exception as e:
        print(f"❌ 스케줄 크롤링 오류: {e}")

async def update_scheduler(settings: dict):
    """스케줄러 업데이트"""
    try:
        # 기존 작업 제거
        scheduler.remove_all_jobs()
        
        if not settings.get('enabled'):
            print("⚠️ 스케줄러 비활성화됨")
            return
        
        # 요일을 cron 형식으로 변환
        day_mapping = {
            'monday': 0,
            'tuesday': 1,
            'wednesday': 2,
            'thursday': 3,
            'friday': 4,
            'saturday': 5,
            'sunday': 6
        }
        
        days = settings.get('days', [])
        day_of_week = ','.join([str(day_mapping[day]) for day in days if day in day_mapping])
        
        # 시간 파싱
        time_str = settings.get('time', '09:00')
        hour, minute = time_str.split(':')
        
        # Cron 트리거 생성
        trigger = CronTrigger(
            day_of_week=day_of_week,
            hour=int(hour),
            minute=int(minute)
        )
        
        # 작업 추가
        scheduler.add_job(
            scheduled_crawl_job,
            trigger,
            id='daily_crawl',
            replace_existing=True
        )
        
        print(f"✅ 스케줄러 등록: 매일 {time_str}, 요일: {day_of_week}")
        
    except Exception as e:
        print(f"❌ 스케줄러 업데이트 오류: {e}")

# CORS middleware
# 환경 변수에서 허용 도메인 가져오기
ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")
# 공인 IP도 추가
PUBLIC_IP = os.getenv("PUBLIC_IP", "")
if PUBLIC_IP:
    ALLOWED_ORIGINS.extend([
        f"http://{PUBLIC_IP}:3000",
        f"http://{PUBLIC_IP}:8001",
    ])

print(f"🔍 CORS 허용 도메인: {ALLOWED_ORIGINS}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper functions
def verify_password(plain_password: str, stored_password: str) -> bool:
    """간단한 비밀번호 검증 - 평문 비교"""
    print(f"🔍 비밀번호 검증: {plain_password[:3]}... vs {stored_password[:3]}...")
    result = plain_password == stored_password
    print(f"🔍 검증 결과: {result}")
    return result

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
    print(f"🔍 로그인 시도: {login_data.username}")
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, username, email, hashed_password, is_active
            FROM users
            WHERE username = :username AND is_active = 1
        """), {"username": login_data.username})
        
        user = result.fetchone()
        print(f"🔍 사용자 조회 결과: {user}")
        
        if not user:
            print("❌ 사용자를 찾을 수 없습니다.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # 비밀번호 검증 (간단한 해시 비교)
        stored_password = user[3]
        print(f"🔍 저장된 비밀번호 해시: {stored_password}")
        
        if not verify_password(login_data.password, stored_password):
            print("❌ 비밀번호가 일치하지 않습니다.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # JWT 토큰 생성
        access_token = create_access_token(data={"sub": user[1]})
        print(f"✅ 로그인 성공: {user[1]}")
        
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

@app.get("/api/dashboard/recent-activity", response_model=List[RecentActivity])
async def get_recent_activity(limit: int = 10, current_user: UserResponse = Depends(get_current_user)):
    """최근 활동 조회"""
    print(f"🔍 get_recent_activity 호출됨 (limit={limit})")
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT cr.id, k.keyword, b.name as blog_name, cr.status, cr.created_at
            FROM crawl_runs cr
            JOIN keywords k ON cr.keyword_id = k.id
            JOIN blogs b ON cr.blog_id = b.id
            ORDER BY cr.created_at DESC
            LIMIT :limit
        """), {"limit": limit})
        
        activities = []
        for row in result:
            activities.append(RecentActivity(
                id=row[0],
                keyword=row[1],
                blog_name=row[2],
                status=row[3],
                created_at=str(row[4])
            ))
        
        print(f"✅ 최근 활동 조회 성공: {len(activities)}개")
        return activities

# Keywords API endpoints
@app.get("/api/keywords", response_model=List[KeywordResponse])
async def get_keywords(current_user: UserResponse = Depends(get_current_user)):
    """키워드 목록 조회"""
    print(f"🔍 get_keywords 호출됨")
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, keyword, description, is_active, created_at, updated_at
            FROM keywords
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
        
        print(f"✅ 키워드 조회 성공: {len(keywords)}개")
        return keywords

@app.post("/api/keywords", response_model=KeywordResponse)
async def create_keyword(keyword_data: KeywordCreate, current_user: UserResponse = Depends(get_current_user)):
    """키워드 생성"""
    print(f"🔍 create_keyword 호출됨: {keyword_data.keyword}")
    
    with engine.connect() as conn:
        # 중복 키워드 확인
        result = conn.execute(text("""
            SELECT id FROM keywords WHERE keyword = :keyword
        """), {"keyword": keyword_data.keyword})
        
        if result.fetchone():
            print(f"❌ 중복 키워드: {keyword_data.keyword}")
            raise HTTPException(status_code=400, detail="이미 존재하는 키워드입니다")
        
        # 키워드 생성
        result = conn.execute(text("""
            INSERT INTO keywords (keyword, description, is_active)
            VALUES (:keyword, :description, 1)
        """), {
            "keyword": keyword_data.keyword,
            "description": keyword_data.description
        })
        
        conn.commit()
        
        # 생성된 키워드 조회
        result = conn.execute(text("""
            SELECT id, keyword, description, is_active, created_at, updated_at
            FROM keywords
            WHERE keyword = :keyword
        """), {"keyword": keyword_data.keyword})
        
        row = result.fetchone()
        keyword = KeywordResponse(
            id=row[0],
            keyword=row[1],
            description=row[2],
            is_active=bool(row[3]),
            created_at=str(row[4]),
            updated_at=str(row[5])
        )
        
        print(f"✅ 키워드 생성 성공: {keyword.keyword}")
        return keyword

@app.put("/api/keywords/{keyword_id}", response_model=KeywordResponse)
async def update_keyword(keyword_id: int, keyword_data: KeywordUpdate, current_user: UserResponse = Depends(get_current_user)):
    """키워드 수정"""
    print(f"🔍 update_keyword 호출됨: {keyword_id}")
    
    with engine.connect() as conn:
        # 키워드 존재 확인
        result = conn.execute(text("""
            SELECT id FROM keywords WHERE id = :id
        """), {"id": keyword_id})
        
        if not result.fetchone():
            print(f"❌ 키워드 없음: {keyword_id}")
            raise HTTPException(status_code=404, detail="키워드를 찾을 수 없습니다")
        
        # 키워드 수정
        update_fields = []
        params = {"id": keyword_id}
        
        if keyword_data.keyword is not None:
            update_fields.append("keyword = :keyword")
            params["keyword"] = keyword_data.keyword
        
        if keyword_data.description is not None:
            update_fields.append("description = :description")
            params["description"] = keyword_data.description
        
        if keyword_data.is_active is not None:
            update_fields.append("is_active = :is_active")
            params["is_active"] = keyword_data.is_active
        
        if update_fields:
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            query = f"UPDATE keywords SET {', '.join(update_fields)} WHERE id = :id"
            conn.execute(text(query), params)
            conn.commit()
        
        # 수정된 키워드 조회
        result = conn.execute(text("""
            SELECT id, keyword, description, is_active, created_at, updated_at
            FROM keywords
            WHERE id = :id
        """), {"id": keyword_id})
        
        row = result.fetchone()
        keyword = KeywordResponse(
            id=row[0],
            keyword=row[1],
            description=row[2],
            is_active=bool(row[3]),
            created_at=str(row[4]),
            updated_at=str(row[5])
        )
        
        print(f"✅ 키워드 수정 성공: {keyword.keyword}")
        return keyword

@app.delete("/api/keywords/{keyword_id}")
async def delete_keyword(keyword_id: int, current_user: UserResponse = Depends(get_current_user)):
    """키워드 삭제"""
    print(f"🔍 delete_keyword 호출됨: {keyword_id}")
    
    with engine.connect() as conn:
        # 키워드 존재 확인
        result = conn.execute(text("""
            SELECT keyword FROM keywords WHERE id = :id
        """), {"id": keyword_id})
        
        row = result.fetchone()
        if not row:
            print(f"❌ 키워드 없음: {keyword_id}")
            raise HTTPException(status_code=404, detail="키워드를 찾을 수 없습니다")
        
        keyword_name = row[0]
        
        # 키워드 삭제
        conn.execute(text("""
            DELETE FROM keywords WHERE id = :id
        """), {"id": keyword_id})
        
        conn.commit()
        
        print(f"✅ 키워드 삭제 성공: {keyword_name}")
        return {"message": "키워드가 삭제되었습니다"}

@app.post("/api/keywords/upload-excel")
async def upload_keywords_excel(file: UploadFile = File(...), current_user: UserResponse = Depends(get_current_user)):
    """엑셀 파일로 키워드 일괄 업로드"""
    print(f"🔍 upload_keywords_excel 호출됨: {file.filename}")
    
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(status_code=400, detail="엑셀 파일(.xlsx, .xls) 또는 CSV 파일(.csv)만 업로드 가능합니다")
    
    try:
        # 파일 내용 읽기
        contents = await file.read()
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        else:
            df = pd.read_excel(io.BytesIO(contents))
        
        # 컬럼 확인
        required_columns = ['keyword']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(
                status_code=400, 
                detail=f"엑셀 파일에 '{required_columns[0]}' 컬럼이 필요합니다. 현재 컬럼: {list(df.columns)}"
            )
        
        # description 컬럼이 없으면 추가
        if 'description' not in df.columns:
            df['description'] = ''
        
        # 빈 값 제거
        df = df.dropna(subset=['keyword'])
        df = df[df['keyword'].str.strip() != '']
        
        if len(df) == 0:
            raise HTTPException(status_code=400, detail="유효한 키워드가 없습니다")
        
        # 키워드 일괄 추가
        success_count = 0
        error_count = 0
        errors = []
        
        with engine.connect() as conn:
            for index, row in df.iterrows():
                try:
                    keyword = str(row['keyword']).strip()
                    description = str(row.get('description', '')).strip() if pd.notna(row.get('description')) else ''
                    
                    # 중복 키워드 확인
                    result = conn.execute(text("""
                        SELECT id FROM keywords WHERE keyword = :keyword
                    """), {"keyword": keyword})
                    
                    if result.fetchone():
                        error_count += 1
                        errors.append(f"'{keyword}': 이미 존재하는 키워드")
                        continue
                    
                    # 키워드 추가
                    conn.execute(text("""
                        INSERT INTO keywords (keyword, description, is_active)
                        VALUES (:keyword, :description, 1)
                    """), {
                        "keyword": keyword,
                        "description": description
                    })
                    
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    errors.append(f"'{row['keyword']}': {str(e)}")
            
            conn.commit()
        
        print(f"✅ 엑셀 업로드 완료: 성공 {success_count}개, 실패 {error_count}개")
        
        return {
            "message": f"키워드 업로드 완료: 성공 {success_count}개, 실패 {error_count}개",
            "success_count": success_count,
            "error_count": error_count,
            "errors": errors[:10] if errors else []  # 최대 10개 오류만 반환
        }
        
    except Exception as e:
        print(f"❌ 엑셀 업로드 오류: {e}")
        raise HTTPException(status_code=500, detail=f"파일 처리 중 오류가 발생했습니다: {str(e)}")

# Crawling API endpoints
@app.post("/api/crawl/trigger")
async def trigger_crawl(crawl_request: CrawlRequest, current_user: UserResponse = Depends(get_current_user)):
    """크롤링 실행"""
    print(f"🔍 trigger_crawl 호출됨: {crawl_request}")
    
    try:
        with engine.connect() as conn:
            if crawl_request.target_id:
                # 특정 타겟 크롤링
                result = conn.execute(text("""
                    SELECT kt.id, k.keyword, b.name as blog_name, k.id as keyword_id, b.id as blog_id
                    FROM keyword_targets kt
                    JOIN keywords k ON kt.keyword_id = k.id
                    JOIN blogs b ON kt.blog_id = b.id
                    WHERE kt.id = :target_id AND kt.is_active = 1
                """), {"target_id": crawl_request.target_id})
                
                target_data = result.fetchone()
                if not target_data:
                    raise HTTPException(status_code=404, detail="타겟을 찾을 수 없습니다")
                
                target_id, keyword, blog_name, k_id, b_id = target_data
                
                # 크롤링 실행 기록 생성
                result = conn.execute(text("""
                    INSERT INTO crawl_runs (keyword_id, blog_id, status, started_at)
                    VALUES (:keyword_id, :blog_id, 'running', CURRENT_TIMESTAMP)
                """), {"keyword_id": k_id, "blog_id": b_id})
                
                run_id = result.lastrowid
                conn.commit()
                
                print(f"🔍 타겟 크롤링 실행: {keyword} - {blog_name} (run_id: {run_id})")
                
                # 백그라운드에서 크롤링 실행 (순차적으로)
                await run_crawl_task(run_id, keyword, blog_name, k_id, b_id)
                
                return {"message": f"크롤링이 완료되었습니다: {keyword} - {blog_name}", "run_id": run_id}
                
            elif crawl_request.keyword_id:
                # 특정 키워드의 모든 타겟 크롤링
                result = conn.execute(text("""
                    SELECT kt.id, k.keyword, b.name as blog_name, k.id as keyword_id, b.id as blog_id
                    FROM keyword_targets kt
                    JOIN keywords k ON kt.keyword_id = k.id
                    JOIN blogs b ON kt.blog_id = b.id
                    WHERE k.id = :keyword_id AND kt.is_active = 1
                """), {"keyword_id": crawl_request.keyword_id})
                
                targets = result.fetchall()
                if not targets:
                    raise HTTPException(status_code=404, detail="키워드에 대한 타겟을 찾을 수 없습니다")
                
                run_ids = []
                conn.commit()  # 먼저 모든 실행 기록 생성
                
                # 순차적으로 크롤링 실행
                for target in targets:
                    target_id, keyword, blog_name, k_id, b_id = target
                    
                    # 크롤링 실행 기록 생성
                    result = conn.execute(text("""
                        INSERT INTO crawl_runs (keyword_id, blog_id, status, started_at)
                        VALUES (:keyword_id, :blog_id, 'running', CURRENT_TIMESTAMP)
                    """), {"keyword_id": k_id, "blog_id": b_id})
                    
                    run_id = result.lastrowid
                    run_ids.append(run_id)
                    conn.commit()
                    
                    # 순차적으로 크롤링 실행
                    await run_crawl_task(run_id, keyword, blog_name, k_id, b_id)
                
                return {"message": f"크롤링이 완료되었습니다: {len(targets)}개 타겟", "run_ids": run_ids}
                
            else:
                # 전체 크롤링
                result = conn.execute(text("""
                    SELECT kt.id, k.keyword, b.name as blog_name, k.id as keyword_id, b.id as blog_id
                    FROM keyword_targets kt
                    JOIN keywords k ON kt.keyword_id = k.id
                    JOIN blogs b ON kt.blog_id = b.id
                    WHERE kt.is_active = 1
                """))
                
                targets = result.fetchall()
                if not targets:
                    raise HTTPException(status_code=404, detail="활성 타겟이 없습니다")
                
                run_ids = []
                conn.commit()  # 먼저 모든 실행 기록 생성
                
                # 순차적으로 크롤링 실행 (최대 10개만)
                limited_targets = targets[:10]  # 안정성을 위해 최대 10개만 처리
                
                for target in limited_targets:
                    target_id, keyword, blog_name, k_id, b_id = target
                    
                    # 크롤링 실행 기록 생성
                    result = conn.execute(text("""
                        INSERT INTO crawl_runs (keyword_id, blog_id, status, started_at)
                        VALUES (:keyword_id, :blog_id, 'running', CURRENT_TIMESTAMP)
                    """), {"keyword_id": k_id, "blog_id": b_id})
                    
                    run_id = result.lastrowid
                    run_ids.append(run_id)
                    conn.commit()
                    
                    # 순차적으로 크롤링 실행
                    await run_crawl_task(run_id, keyword, blog_name, k_id, b_id)
                
                return {"message": f"전체 크롤링이 완료되었습니다: {len(limited_targets)}개 타겟 (총 {len(targets)}개 중)", "run_ids": run_ids}
                
    except Exception as e:
        print(f"❌ 크롤링 시작 오류: {e}")
        raise HTTPException(status_code=500, detail=f"크롤링 시작 중 오류가 발생했습니다: {str(e)}")

def generate_mock_blog_post(keyword: str) -> Dict:
    """테스트용 Mock 블로그 글 생성 (OpenAI API 없이 사용)"""
    print(f"🧪 테스트 모드: Mock 블로그 글 생성 - {keyword}")
    
    # DSL 형식의 Mock 블로그 글
    mock_content = f"""[title]{keyword} 완벽 가이드 - 초보자부터 실전까지[/title]
[separator=line3][/separator]

안녕하세요! 오늘은 [underline]{keyword}[/underline]에 대해 자세히 알아보는 시간을 가져보겠습니다. 이 가이드를 통해 {keyword}의 기초부터 실전까지 완벽하게 이해하실 수 있습니다.

[separator=line3][/separator]
[bold]1. {keyword}란 무엇인가요?[/bold]

{keyword}는 현대 사회에서 매우 중요한 주제입니다. 많은 분들이 {keyword}에 관심을 가지고 계시는데요, 그 이유는 실생활에 바로 적용할 수 있는 실용적인 내용이기 때문입니다.

{keyword}를 처음 접하시는 분들도 쉽게 이해하실 수 있도록 기초부터 차근차근 설명드리겠습니다.

[quote={keyword}는 단순히 배우는 것을 넘어 실제로 활용할 수 있어야 진정한 가치를 발휘합니다]

[separator=line3][/separator]
[bold]2. {keyword}의 핵심 포인트[/bold]

{keyword}를 제대로 이해하기 위해서는 다음 3가지 핵심 포인트를 알아야 합니다.

첫째, 기본 개념을 정확히 이해하는 것이 중요합니다. 기초가 탄탄해야 응용도 쉽게 할 수 있습니다.

둘째, 실전 경험이 필수적입니다. 이론만으로는 부족하며, 직접 해보면서 배우는 것이 가장 효과적입니다.

셋째, 지속적인 학습이 필요합니다. {keyword}는 계속 발전하고 있기 때문에 꾸준한 관심과 학습이 중요합니다.

[separator=line3][/separator]
[bold]3. {keyword} 시작하기[/bold]

이제 본격적으로 {keyword}를 시작해볼까요? 초보자분들도 쉽게 따라하실 수 있는 단계별 가이드를 준비했습니다.

먼저 기본적인 준비사항을 확인해보겠습니다. 필요한 도구나 지식이 있다면 미리 준비하시면 좋습니다.

그 다음으로는 간단한 예제부터 시작하는 것을 추천드립니다. 처음부터 어려운 것에 도전하기보다는 쉬운 것부터 하나씩 익혀나가시는 것이 좋습니다.

[separator=line3][/separator]
[bold]4. 실전 활용 방법[/bold]

{keyword}를 실제로 어떻게 활용할 수 있을까요? 여기 몇 가지 실전 활용 사례를 소개해드립니다.

실무에서는 이론과 다른 상황들을 많이 마주하게 됩니다. 그럴 때마다 당황하지 마시고, 기본 원칙을 떠올리며 차근차근 해결해나가시면 됩니다.

또한 다른 사람들의 경험담을 참고하는 것도 큰 도움이 됩니다. 커뮤니티나 블로그를 통해 다양한 사례를 접해보시기 바랍니다.

[separator=line3][/separator]
[bold]5. 자주 묻는 질문 (FAQ)[/bold]

Q1. {keyword}를 처음 시작하는데 어디서부터 해야 할까요?
A1. 기초 개념부터 차근차근 시작하시는 것을 추천드립니다.

Q2. 얼마나 시간이 걸릴까요?
A2. 개인차가 있지만, 꾸준히 하시면 3-6개월 정도면 기본은 익히실 수 있습니다.

Q3. 혼자서도 가능한가요?
A3. 네, 충분히 가능합니다. 다만 커뮤니티나 스터디 그룹을 활용하시면 더 효과적입니다.

[separator=line3][/separator]
[bold]마무리[/bold]

지금까지 {keyword}에 대해 알아보았습니다. 이 가이드가 {keyword}를 시작하시는 분들에게 도움이 되었으면 좋겠습니다.

중요한 것은 [italic]꾸준함[/italic]입니다. 조금씩이라도 매일 실천하다 보면 어느새 큰 발전을 이루실 수 있을 것입니다.

여러분의 {keyword} 여정을 응원합니다! 화이팅! 💪"""

    return {
        "title": f"[title]{keyword} 완벽 가이드 - 초보자부터 실전까지[/title]",
        "content": mock_content,
        "summary": f"{keyword}에 대한 초보자를 위한 완벽한 가이드입니다. 기초 개념부터 실전 활용까지 단계별로 자세히 설명합니다.",
        "tags": [keyword, "가이드", "초보자", "완벽정리", "실전활용"]
    }

async def check_target_blog_in_results(keyword_id: int, run_id: int) -> bool:
    """크롤링 결과에 타겟 블로그가 있는지 확인"""
    try:
        with engine.connect() as conn:
            # 등록된 타겟 블로그 URL 패턴 가져오기
            targets_result = conn.execute(
                text("""
                    SELECT b.url_pattern 
                    FROM keyword_targets kt
                    JOIN blogs b ON kt.blog_id = b.id
                    WHERE kt.keyword_id = :keyword_id AND kt.is_active = 1
                """),
                {"keyword_id": keyword_id}
            )
            target_patterns = [row[0] for row in targets_result.fetchall()]
            
            if not target_patterns:
                return True  # 타겟이 없으면 확인 불필요
            
            # 크롤링 결과에서 타겟 블로그 확인
            results = conn.execute(
                text("SELECT url FROM crawl_results WHERE crawl_run_id = :run_id"),
                {"run_id": run_id}
            )
            
            for result in results:
                url = result[0]
                for pattern in target_patterns:
                    if pattern in url:
                        return True  # 타겟 블로그 발견
            
            return False  # 타겟 블로그 없음
            
    except Exception as e:
        print(f"❌ 타겟 블로그 확인 오류: {e}")
        return True  # 오류 시 확인 통과

async def generate_blog_post_ai(keyword: str) -> Optional[Dict]:
    """AI를 사용한 블로그 글 생성"""
    openai_key = os.getenv("OPENAI_API_KEY", "")
    
    # OpenAI API가 없으면 테스트용 Mock 데이터 생성
    if not OPENAI_AVAILABLE or not openai_key:
        print("⚠️ OpenAI API를 사용할 수 없습니다. 테스트 모드로 블로그 글을 생성합니다.")
        return generate_mock_blog_post(keyword)
    
    try:
        openai.api_key = openai_key
        
        system_prompt = """You are a strict DSL formatter and professional Korean blog writer. Output must use DSL only.

[DSL Rules]
- Allowed tags: [title][/title], [bold][/bold], [underline][/underline], [italic][/italic], [align=center]...[/align], [separator=LINE][/separator], [quote=TEXT], [img=INDEXES layout=collage][/img]
- Tags must be properly closed, no unnecessary spaces between tags
- Do NOT use Markdown, HTML, code blocks, backticks, links, or image syntax
- Write in Korean only

[Parameter Rules]
- [separator=LINE]: LINE must be exactly one of: line1, line2, line3, line4, line5, line6, line7. Never output "line1~7". Use line3 if uncertain.
- [img=INDEXES layout=collage]: INDEXES must be comma-separated integers (e.g., "1,2" or "3,4"). Use at most two images per tag.

[Writing Rules]
- Length: 1200–1600 characters (Korean characters)
- Tone: professional but friendly, polite Korean (존댓말)
- Structure: Introduction → Main body (3–5 subheadings) → Checklist/Summary → Conclusion
- SEO: include keyword naturally in first paragraph and subheadings (2–3 times total)
- Title uses [title], subheadings use [bold]
- Use [underline], [italic], [quote] for emphasis
- Use [separator] for visual breaks between sections
- [img] can be used 0–2 times (omit if not needed)

[Output Format]
Return JSON only:
{
    "title": "DSL formatted title with [title] tags",
    "content": "Full DSL formatted blog post",
    "summary": "Brief summary 100-150 characters",
    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
}"""
        
        user_prompt = f"""Write a blog post for this keyword: "{keyword}"

Requirements:
1. Use DSL format strictly (no Markdown)
2. Start with [title]...[/title]
3. First paragraph must include keyword "{keyword}"
4. 3-5 subheadings with [bold]...[/bold]
5. Each section 2-3 paragraphs
6. Use [separator=line3] between major sections
7. Include practical tips or checklist
8. End with friendly conclusion
9. Add [quote=...] for key points
10. Output as JSON with "title", "content", "summary", "tags"

Example DSL structure:
[title]제목[/title]
[separator=line3][/separator]
[bold]소제목 1[/bold]
본문 내용...
[quote=핵심 포인트]
[separator=line3][/separator]
[bold]소제목 2[/bold]
본문 내용...

Write in Korean, 1200-1600 characters."""
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            max_tokens=2500,
            temperature=0.7,
        )
        
        content = response.choices[0].message.content
        
        # JSON 파싱
        import json
        if "```json" in content:
            json_start = content.find("```json") + 7
            json_end = content.find("```", json_start)
            json_str = content[json_start:json_end].strip()
        else:
            json_str = content.strip()
        
        result = json.loads(json_str)
        return result
        
    except Exception as e:
        print(f"❌ AI 블로그 글 생성 오류: {e}")
        return None

async def run_crawl_task(run_id: int, keyword: str, blog_name: str, keyword_id: int, blog_id: int):
    """백그라운드 크롤링 작업"""
    print(f"🔍 크롤링 작업 시작: {keyword} - {blog_name} (run_id: {run_id})")
    
    try:
        # 크롤링 실행
        results = await crawl_keyword_async(keyword)
        
        # 결과 저장
        with engine.connect() as conn:
            rank = 1
            for section in results:
                section_name = section.get("span", "Unknown")  # 섹션 이름 가져오기
                
                for article_box in section.get("article_boxes", []):
                    for link in article_box.get("links", []):
                        # 블로그 URL 패턴 확인
                        if any(pattern in link["href"] for pattern in ["blog.naver.com", "tistory.com", "velog.io"]):
                            conn.execute(text("""
                                INSERT INTO crawl_results (crawl_run_id, keyword_id, blog_id, rank, title, url, snippet, section)
                                VALUES (:run_id, :keyword_id, :blog_id, :rank, :title, :url, :snippet, :section)
                            """), {
                                "run_id": run_id,
                                "keyword_id": keyword_id,
                                "blog_id": blog_id,
                                "rank": rank,
                                "title": link["text"],
                                "url": link["href"],
                                "snippet": f"키워드 '{keyword}' 검색 결과",
                                "section": section_name
                            })
                            rank += 1
            
            # 크롤링 완료 상태 업데이트
            conn.execute(text("""
                UPDATE crawl_runs 
                SET status = 'success', completed_at = CURRENT_TIMESTAMP
                WHERE id = :run_id
            """), {"run_id": run_id})
            
            conn.commit()
        
        print(f"✅ 크롤링 작업 완료: {keyword} - {blog_name} (run_id: {run_id})")
        
        # 타겟 블로그 확인 및 자동 글 생성 (설정에 따라)
        ai_settings = get_ai_blog_settings()
        if ai_settings and ai_settings.get('enabled', False):
            has_target = await check_target_blog_in_results(keyword_id, run_id)
            if not has_target:
                print(f"⚠️ 타겟 블로그가 검색 결과에 없습니다: {keyword}")
                print(f"🤖 AI 블로그 글 자동 생성 시작...")
                
                blog_post = await generate_blog_post_ai(keyword)
                if blog_post:
                    # 생성된 글 저장
                    with engine.connect() as conn:
                        import json
                        conn.execute(text("""
                            INSERT INTO generated_posts 
                            (keyword_id, crawl_run_id, title, content, summary, tags, status, created_at)
                            VALUES (:keyword_id, :crawl_run_id, :title, :content, :summary, :tags, 'generated', CURRENT_TIMESTAMP)
                        """), {
                            "keyword_id": keyword_id,
                            "crawl_run_id": run_id,
                            "title": blog_post["title"],
                            "content": blog_post["content"],
                            "summary": blog_post["summary"],
                            "tags": json.dumps(blog_post.get("tags", []), ensure_ascii=False)
                        })
                        conn.commit()
                    
                    print(f"✅ AI 블로그 글 생성 완료: {blog_post['title']}")
                    
                    # SMS 알림 (블로그 글 생성됨)
                    notification_settings = get_notification_settings()
                    if notification_settings and notification_settings.get('enabled'):
                        phone_number = notification_settings.get('phone_number')
                        if phone_number:
                            message = f"[Naver Monitor] 🤖 AI 블로그 글 생성\n키워드: {keyword}\n제목: {blog_post['title']}"
                            await send_sms_notification(phone_number, message)
        
        # 알림 설정 확인 및 SMS 발송
        notification_settings = get_notification_settings()
        if notification_settings and notification_settings.get('enabled') and notification_settings.get('notify_on_success'):
            phone_number = notification_settings.get('phone_number')
            if phone_number:
                message = f"[Naver Monitor] 크롤링 완료\n키워드: {keyword}\n블로그: {blog_name}\n결과: {rank-1}개 발견"
                await send_sms_notification(phone_number, message)
        
    except Exception as e:
        import traceback
        error_details = f"{str(e)}\n\n상세 오류:\n{traceback.format_exc()}"
        print(f"❌ 크롤링 작업 오류: {keyword} - {blog_name} (run_id: {run_id})")
        print(f"오류 내용: {error_details}")
        
        # 오류 상태 업데이트
        with engine.connect() as conn:
            conn.execute(text("""
                UPDATE crawl_runs 
                SET status = 'error', completed_at = CURRENT_TIMESTAMP, error_message = :error_message
                WHERE id = :run_id
            """), {"run_id": run_id, "error_message": error_details})
            conn.commit()
        
        # 알림 설정 확인 및 SMS 발송 (오류 시)
        notification_settings = get_notification_settings()
        if notification_settings and notification_settings.get('enabled') and notification_settings.get('notify_on_error'):
            phone_number = notification_settings.get('phone_number')
            if phone_number:
                error_msg = str(e).split('\n')[0][:100]  # 첫 줄만, 최대 100자
                message = f"[Naver Monitor] 크롤링 실패\n키워드: {keyword}\n블로그: {blog_name}\n오류: {error_msg}"
                await send_sms_notification(phone_number, message)

@app.get("/api/crawl/runs", response_model=List[CrawlRun])
async def get_crawl_runs(limit: int = 50, current_user: UserResponse = Depends(get_current_user)):
    """크롤링 실행 기록 조회"""
    print(f"🔍 get_crawl_runs 호출됨 (limit: {limit})")
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT cr.id, k.keyword, b.name as blog_name, cr.status, cr.started_at, cr.completed_at, cr.error_message, cr.created_at
            FROM crawl_runs cr
            JOIN keywords k ON cr.keyword_id = k.id
            JOIN blogs b ON cr.blog_id = b.id
            ORDER BY cr.created_at DESC
            LIMIT :limit
        """), {"limit": limit})
        
        runs = []
        for row in result:
            runs.append(CrawlRun(
                id=row[0],
                keyword=row[1],
                blog_name=row[2],
                status=row[3],
                started_at=str(row[4]) if row[4] else None,
                completed_at=str(row[5]) if row[5] else None,
                error_message=row[6],
                created_at=str(row[7])
            ))
        
        print(f"✅ 크롤링 실행 기록 조회 성공: {len(runs)}개")
        return runs

@app.get("/api/crawl/results", response_model=List[CrawlResult])
async def get_crawl_results(
    keyword_id: Optional[int] = None,
    blog_id: Optional[int] = None,
    limit: int = 100,
    current_user: UserResponse = Depends(get_current_user)
):
    """크롤링 결과 조회"""
    print(f"🔍 get_crawl_results 호출됨 (keyword_id: {keyword_id}, blog_id: {blog_id}, limit: {limit})")
    
    with engine.connect() as conn:
        query = """
            SELECT cr.id, cr.crawl_run_id, k.keyword, b.name as blog_name, cr.rank, cr.title, cr.url, cr.snippet, cr.section, cr.created_at
            FROM crawl_results cr
            JOIN keywords k ON cr.keyword_id = k.id
            JOIN blogs b ON cr.blog_id = b.id
        """
        params = {"limit": limit}
        
        if keyword_id:
            query += " WHERE cr.keyword_id = :keyword_id"
            params["keyword_id"] = keyword_id
        
        if blog_id:
            if keyword_id:
                query += " AND cr.blog_id = :blog_id"
            else:
                query += " WHERE cr.blog_id = :blog_id"
            params["blog_id"] = blog_id
        
        query += " ORDER BY cr.created_at DESC, cr.rank ASC LIMIT :limit"
        
        result = conn.execute(text(query), params)
        
        results = []
        for row in result:
            results.append(CrawlResult(
                id=row[0],
                crawl_run_id=row[1],
                keyword=row[2],
                blog_name=row[3],
                rank=row[4],
                title=row[5],
                url=row[6],
                snippet=row[7],
                section=row[8],
                created_at=str(row[9])
            ))
        
        print(f"✅ 크롤링 결과 조회 성공: {len(results)}개")
        return results

# Blogs API endpoints
@app.get("/api/blogs", response_model=List[BlogResponse])
async def get_blogs(current_user: UserResponse = Depends(get_current_user)):
    """블로그 목록 조회"""
    print(f"🔍 get_blogs 호출됨")
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, name, url_pattern, description, is_active, created_at, updated_at
            FROM blogs
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
        
        print(f"✅ 블로그 조회 성공: {len(blogs)}개")
        return blogs

@app.post("/api/blogs", response_model=BlogResponse)
async def create_blog(blog_data: BlogCreate, current_user: UserResponse = Depends(get_current_user)):
    """블로그 생성"""
    print(f"🔍 create_blog 호출됨: {blog_data.name}")
    
    with engine.connect() as conn:
        # 중복 블로그 확인
        result = conn.execute(text("""
            SELECT id FROM blogs WHERE name = :name OR url_pattern = :url_pattern
        """), {"name": blog_data.name, "url_pattern": blog_data.url_pattern})
        
        if result.fetchone():
            print(f"❌ 중복 블로그: {blog_data.name} 또는 {blog_data.url_pattern}")
            raise HTTPException(status_code=400, detail="이미 존재하는 블로그 이름 또는 URL 패턴입니다")
        
        # 블로그 생성
        result = conn.execute(text("""
            INSERT INTO blogs (name, url_pattern, description, is_active)
            VALUES (:name, :url_pattern, :description, 1)
        """), {
            "name": blog_data.name,
            "url_pattern": blog_data.url_pattern,
            "description": blog_data.description
        })
        
        conn.commit()
        
        # 생성된 블로그 조회
        result = conn.execute(text("""
            SELECT id, name, url_pattern, description, is_active, created_at, updated_at
            FROM blogs
            WHERE name = :name
        """), {"name": blog_data.name})
        
        row = result.fetchone()
        blog = BlogResponse(
            id=row[0],
            name=row[1],
            url_pattern=row[2],
            description=row[3],
            is_active=bool(row[4]),
            created_at=str(row[5]),
            updated_at=str(row[6])
        )
        
        print(f"✅ 블로그 생성 성공: {blog.name}")
        return blog

@app.put("/api/blogs/{blog_id}", response_model=BlogResponse)
async def update_blog(blog_id: int, blog_data: BlogUpdate, current_user: UserResponse = Depends(get_current_user)):
    """블로그 수정"""
    print(f"🔍 update_blog 호출됨: {blog_id}")
    
    with engine.connect() as conn:
        # 블로그 존재 확인
        result = conn.execute(text("""
            SELECT id FROM blogs WHERE id = :id
        """), {"id": blog_id})
        
        if not result.fetchone():
            print(f"❌ 블로그 없음: {blog_id}")
            raise HTTPException(status_code=404, detail="블로그를 찾을 수 없습니다")
        
        # 블로그 수정
        update_fields = []
        params = {"id": blog_id}
        
        if blog_data.name is not None:
            update_fields.append("name = :name")
            params["name"] = blog_data.name
        
        if blog_data.url_pattern is not None:
            update_fields.append("url_pattern = :url_pattern")
            params["url_pattern"] = blog_data.url_pattern
        
        if blog_data.description is not None:
            update_fields.append("description = :description")
            params["description"] = blog_data.description
        
        if blog_data.is_active is not None:
            update_fields.append("is_active = :is_active")
            params["is_active"] = blog_data.is_active
        
        if update_fields:
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            query = f"UPDATE blogs SET {', '.join(update_fields)} WHERE id = :id"
            conn.execute(text(query), params)
            conn.commit()
        
        # 수정된 블로그 조회
        result = conn.execute(text("""
            SELECT id, name, url_pattern, description, is_active, created_at, updated_at
            FROM blogs
            WHERE id = :id
        """), {"id": blog_id})
        
        row = result.fetchone()
        blog = BlogResponse(
            id=row[0],
            name=row[1],
            url_pattern=row[2],
            description=row[3],
            is_active=bool(row[4]),
            created_at=str(row[5]),
            updated_at=str(row[6])
        )
        
        print(f"✅ 블로그 수정 성공: {blog.name}")
        return blog

@app.delete("/api/blogs/{blog_id}")
async def delete_blog(blog_id: int, current_user: UserResponse = Depends(get_current_user)):
    """블로그 삭제"""
    print(f"🔍 delete_blog 호출됨: {blog_id}")
    
    with engine.connect() as conn:
        # 블로그 존재 확인
        result = conn.execute(text("""
            SELECT name FROM blogs WHERE id = :id
        """), {"id": blog_id})
        
        row = result.fetchone()
        if not row:
            print(f"❌ 블로그 없음: {blog_id}")
            raise HTTPException(status_code=404, detail="블로그를 찾을 수 없습니다")
        
        blog_name = row[0]
        
        # 관련 타겟이 있는지 확인
        result = conn.execute(text("""
            SELECT COUNT(*) FROM keyword_targets kt
            JOIN blogs b ON kt.blog_id = b.id
            WHERE b.id = :blog_id
        """), {"blog_id": blog_id})
        
        target_count = result.fetchone()[0]
        if target_count > 0:
            print(f"❌ 관련 타겟 존재: {target_count}개")
            raise HTTPException(
                status_code=400, 
                detail=f"이 블로그와 연결된 타겟이 {target_count}개 있습니다. 먼저 타겟을 삭제해주세요."
            )
        
        # 블로그 삭제
        conn.execute(text("""
            DELETE FROM blogs WHERE id = :id
        """), {"id": blog_id})
        
        conn.commit()
        
        print(f"✅ 블로그 삭제 성공: {blog_name}")
        return {"message": "블로그가 삭제되었습니다"}

# Targets API endpoints
class TargetCreate(BaseModel):
    keyword_id: int
    blog_id: int

class TargetUpdate(BaseModel):
    is_active: Optional[bool] = None

class TargetResponse(BaseModel):
    id: int
    keyword_id: int
    blog_id: int
    keyword: Optional[str]
    blog_name: Optional[str]
    is_active: bool
    created_at: str
    updated_at: str

@app.get("/api/targets", response_model=List[TargetResponse])
async def get_targets(current_user: UserResponse = Depends(get_current_user)):
    """타겟 목록 조회"""
    print(f"🔍 get_targets 호출됨")
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT kt.id, kt.keyword_id, kt.blog_id, k.keyword, b.name as blog_name, 
                   kt.is_active, kt.created_at, kt.updated_at
            FROM keyword_targets kt
            JOIN keywords k ON kt.keyword_id = k.id
            JOIN blogs b ON kt.blog_id = b.id
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
        
        print(f"✅ 타겟 조회 성공: {len(targets)}개")
        return targets

@app.post("/api/targets", response_model=TargetResponse)
async def create_target(target_data: TargetCreate, current_user: UserResponse = Depends(get_current_user)):
    """타겟 생성"""
    print(f"🔍 create_target 호출됨: keyword_id={target_data.keyword_id}, blog_id={target_data.blog_id}")
    
    with engine.connect() as conn:
        # 중복 타겟 확인
        result = conn.execute(text("""
            SELECT id FROM keyword_targets 
            WHERE keyword_id = :keyword_id AND blog_id = :blog_id
        """), {"keyword_id": target_data.keyword_id, "blog_id": target_data.blog_id})
        
        if result.fetchone():
            print(f"❌ 중복 타겟: keyword_id={target_data.keyword_id}, blog_id={target_data.blog_id}")
            raise HTTPException(status_code=400, detail="이미 존재하는 타겟입니다")
        
        # 타겟 생성
        result = conn.execute(text("""
            INSERT INTO keyword_targets (keyword_id, blog_id, is_active)
            VALUES (:keyword_id, :blog_id, 1)
        """), {
            "keyword_id": target_data.keyword_id,
            "blog_id": target_data.blog_id
        })
        
        conn.commit()
        
        # 생성된 타겟 조회
        result = conn.execute(text("""
            SELECT kt.id, kt.keyword_id, kt.blog_id, k.keyword, b.name as blog_name, 
                   kt.is_active, kt.created_at, kt.updated_at
            FROM keyword_targets kt
            JOIN keywords k ON kt.keyword_id = k.id
            JOIN blogs b ON kt.blog_id = b.id
            WHERE kt.keyword_id = :keyword_id AND kt.blog_id = :blog_id
        """), {"keyword_id": target_data.keyword_id, "blog_id": target_data.blog_id})
        
        row = result.fetchone()
        target = TargetResponse(
            id=row[0],
            keyword_id=row[1],
            blog_id=row[2],
            keyword=row[3],
            blog_name=row[4],
            is_active=bool(row[5]),
            created_at=str(row[6]),
            updated_at=str(row[7])
        )
        
        print(f"✅ 타겟 생성 성공: {target.keyword} - {target.blog_name}")
        return target

@app.put("/api/targets/{target_id}", response_model=TargetResponse)
async def update_target(target_id: int, target_data: TargetUpdate, current_user: UserResponse = Depends(get_current_user)):
    """타겟 수정"""
    print(f"🔍 update_target 호출됨: {target_id}")
    
    with engine.connect() as conn:
        # 타겟 존재 확인
        result = conn.execute(text("""
            SELECT id FROM keyword_targets WHERE id = :id
        """), {"id": target_id})
        
        if not result.fetchone():
            print(f"❌ 타겟 없음: {target_id}")
            raise HTTPException(status_code=404, detail="타겟을 찾을 수 없습니다")
        
        # 타겟 수정
        update_fields = []
        params = {"id": target_id}
        
        if target_data.is_active is not None:
            update_fields.append("is_active = :is_active")
            params["is_active"] = target_data.is_active
        
        if update_fields:
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            query = f"UPDATE keyword_targets SET {', '.join(update_fields)} WHERE id = :id"
            conn.execute(text(query), params)
            conn.commit()
        
        # 수정된 타겟 조회
        result = conn.execute(text("""
            SELECT kt.id, kt.keyword_id, kt.blog_id, k.keyword, b.name as blog_name, 
                   kt.is_active, kt.created_at, kt.updated_at
            FROM keyword_targets kt
            JOIN keywords k ON kt.keyword_id = k.id
            JOIN blogs b ON kt.blog_id = b.id
            WHERE kt.id = :id
        """), {"id": target_id})
        
        row = result.fetchone()
        target = TargetResponse(
            id=row[0],
            keyword_id=row[1],
            blog_id=row[2],
            keyword=row[3],
            blog_name=row[4],
            is_active=bool(row[5]),
            created_at=str(row[6]),
            updated_at=str(row[7])
        )
        
        print(f"✅ 타겟 수정 성공: {target.keyword} - {target.blog_name}")
        return target

@app.delete("/api/targets/{target_id}")
async def delete_target(target_id: int, current_user: UserResponse = Depends(get_current_user)):
    """타겟 삭제"""
    print(f"🔍 delete_target 호출됨: {target_id}")
    
    with engine.connect() as conn:
        # 타겟 존재 확인
        result = conn.execute(text("""
            SELECT k.keyword, b.name as blog_name
            FROM keyword_targets kt
            JOIN keywords k ON kt.keyword_id = k.id
            JOIN blogs b ON kt.blog_id = b.id
            WHERE kt.id = :id
        """), {"id": target_id})
        
        row = result.fetchone()
        if not row:
            print(f"❌ 타겟 없음: {target_id}")
            raise HTTPException(status_code=404, detail="타겟을 찾을 수 없습니다")
        
        keyword_name, blog_name = row
        
        # 타겟 삭제
        conn.execute(text("""
            DELETE FROM keyword_targets WHERE id = :id
        """), {"id": target_id})
        
        conn.commit()
        
        print(f"✅ 타겟 삭제 성공: {keyword_name} - {blog_name}")
        return {"message": "타겟이 삭제되었습니다"}

# Settings API endpoints
class NotificationSettings(BaseModel):
    enabled: bool
    phone_number: str
    notification_type: str
    notify_on_success: bool
    notify_on_error: bool

@app.get("/api/settings/notifications")
async def get_notification_settings_api(current_user: UserResponse = Depends(get_current_user)):
    """알림 설정 조회"""
    print(f"🔍 get_notification_settings 호출됨")
    
    settings = get_notification_settings()
    if not settings:
        # 기본 설정 반환
        return {
            "enabled": False,
            "phone_number": "",
            "notification_type": "sms",
            "notify_on_success": True,
            "notify_on_error": True
        }
    
    return settings

@app.post("/api/settings/notifications")
async def save_notification_settings_api(settings: NotificationSettings, current_user: UserResponse = Depends(get_current_user)):
    """알림 설정 저장"""
    print(f"🔍 save_notification_settings 호출됨: {settings}")
    
    settings_dict = {
        "enabled": settings.enabled,
        "phone_number": settings.phone_number,
        "notification_type": settings.notification_type,
        "notify_on_success": settings.notify_on_success,
        "notify_on_error": settings.notify_on_error
    }
    
    save_notification_settings(settings_dict)
    print(f"✅ 알림 설정 저장 완료")
    
    return {"message": "설정이 저장되었습니다", "settings": settings_dict}

@app.post("/api/settings/notifications/test")
async def test_notification(current_user: UserResponse = Depends(get_current_user)):
    """테스트 알림 발송"""
    print(f"🔍 test_notification 호출됨")
    
    settings = get_notification_settings()
    if not settings or not settings.get('enabled'):
        raise HTTPException(status_code=400, detail="알림이 비활성화되어 있습니다")
    
    phone_number = settings.get('phone_number')
    if not phone_number:
        raise HTTPException(status_code=400, detail="전화번호가 설정되지 않았습니다")
    
    message = "[Naver Monitor] 테스트 메시지\n알림 설정이 정상적으로 작동합니다."
    success = await send_sms_notification(phone_number, message)
    
    if success:
        return {"message": f"테스트 메시지를 {phone_number}로 전송했습니다"}
    else:
        raise HTTPException(status_code=500, detail="메시지 전송에 실패했습니다")

# Schedule Settings
class ScheduleSettings(BaseModel):
    enabled: bool
    time: str
    days: List[str]

class AIBlogSettings(BaseModel):
    enabled: bool
    use_openai: bool  # True: OpenAI API 사용, False: Mock 사용
    model: Optional[str] = "gpt-3.5-turbo"
    temperature: Optional[float] = 0.7

@app.get("/api/settings/schedule")
async def get_schedule_settings_api(current_user: UserResponse = Depends(get_current_user)):
    """스케줄 설정 조회"""
    print(f"🔍 get_schedule_settings 호출됨")
    
    settings = get_schedule_settings()
    if not settings:
        # 기본 설정 반환
        return {
            "enabled": False,
            "time": "09:00",
            "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
        }
    
    return settings

@app.post("/api/settings/schedule")
async def save_schedule_settings_api(settings: ScheduleSettings, current_user: UserResponse = Depends(get_current_user)):
    """스케줄 설정 저장"""
    print(f"🔍 save_schedule_settings 호출됨: {settings}")
    
    settings_dict = {
        "enabled": settings.enabled,
        "time": settings.time,
        "days": settings.days
    }
    
    save_schedule_settings(settings_dict)
    
    # 스케줄러 업데이트
    if settings.enabled:
        await update_scheduler(settings_dict)
        print(f"✅ 스케줄러 업데이트 완료: 매일 {settings.time}, 요일: {', '.join(settings.days)}")
    else:
        print(f"⚠️ 스케줄러 비활성화")
    
    return {"message": "스케줄 설정이 저장되었습니다", "settings": settings_dict}

# AI Blog Settings
@app.get("/api/settings/ai-blog")
async def get_ai_blog_settings_api(current_user: UserResponse = Depends(get_current_user)):
    """AI 블로그 설정 조회"""
    print(f"🔍 get_ai_blog_settings 호출됨")
    
    settings = get_ai_blog_settings()
    if not settings:
        # 기본 설정 반환
        return {
            "enabled": False,
            "use_openai": False,
            "model": "gpt-3.5-turbo",
            "temperature": 0.7
        }
    
    return settings

@app.post("/api/settings/ai-blog")
async def save_ai_blog_settings_api(
    settings: AIBlogSettings, 
    current_user: UserResponse = Depends(get_current_user)
):
    """AI 블로그 설정 저장"""
    print(f"🔍 save_ai_blog_settings 호출됨: {settings}")
    
    settings_dict = {
        "enabled": settings.enabled,
        "use_openai": settings.use_openai,
        "model": settings.model or "gpt-3.5-turbo",
        "temperature": settings.temperature or 0.7
    }
    
    save_ai_blog_settings(settings_dict)
    
    mode = "OpenAI API" if settings.use_openai else "Mock (테스트)"
    status = "활성화" if settings.enabled else "비활성화"
    print(f"✅ AI 블로그 설정 업데이트: {status}, 모드: {mode}")
    
    return {"message": "AI 블로그 설정이 저장되었습니다", "settings": settings_dict}

# 생성된 블로그 글 API
@app.get("/api/generated-posts", response_model=List[GeneratedPost])
async def get_generated_posts(
    keyword_id: Optional[int] = None,
    limit: int = 50,
    current_user: UserResponse = Depends(get_current_user)
):
    """생성된 블로그 글 목록 조회"""
    print(f"🔍 get_generated_posts 호출됨 (keyword_id: {keyword_id}, limit: {limit})")
    
    with engine.connect() as conn:
        query = """
            SELECT id, keyword_id, crawl_run_id, title, content, summary, tags, status, created_at, published_at
            FROM generated_posts
        """
        params = {"limit": limit}
        
        if keyword_id:
            query += " WHERE keyword_id = :keyword_id"
            params["keyword_id"] = keyword_id
        
        query += " ORDER BY created_at DESC LIMIT :limit"
        
        result = conn.execute(text(query), params)
        
        posts = []
        for row in result:
            posts.append(GeneratedPost(
                id=row[0],
                keyword_id=row[1],
                crawl_run_id=row[2],
                title=row[3],
                content=row[4],
                summary=row[5],
                tags=row[6],
                status=row[7],
                created_at=str(row[8]),
                published_at=str(row[9]) if row[9] else None
            ))
        
        print(f"✅ 생성된 글 조회 성공: {len(posts)}개")
        return posts

@app.get("/api/generated-posts/{post_id}", response_model=GeneratedPost)
async def get_generated_post(
    post_id: int,
    current_user: UserResponse = Depends(get_current_user)
):
    """생성된 블로그 글 상세 조회"""
    print(f"🔍 get_generated_post 호출됨 (post_id: {post_id})")
    
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT id, keyword_id, crawl_run_id, title, content, summary, tags, status, created_at, published_at
                FROM generated_posts
                WHERE id = :post_id
            """),
            {"post_id": post_id}
        )
        
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="글을 찾을 수 없습니다")
        
        post = GeneratedPost(
            id=row[0],
            keyword_id=row[1],
            crawl_run_id=row[2],
            title=row[3],
            content=row[4],
            summary=row[5],
            tags=row[6],
            status=row[7],
            created_at=str(row[8]),
            published_at=str(row[9]) if row[9] else None
        )
        
        print(f"✅ 글 조회 성공: {post.title}")
        return post

@app.delete("/api/generated-posts/{post_id}")
async def delete_generated_post(
    post_id: int,
    current_user: UserResponse = Depends(get_current_user)
):
    """생성된 블로그 글 삭제"""
    print(f"🔍 delete_generated_post 호출됨 (post_id: {post_id})")
    
    with engine.connect() as conn:
        conn.execute(
            text("DELETE FROM generated_posts WHERE id = :post_id"),
            {"post_id": post_id}
        )
        conn.commit()
        
        print(f"✅ 글 삭제 완료: {post_id}")
        return {"message": "글이 삭제되었습니다"}

@app.post("/api/generated-posts/{post_id}/prepare-publish")
async def prepare_publish_post(
    post_id: int,
    current_user: UserResponse = Depends(get_current_user)
):
    """생성된 글을 발행 준비 (HTML/DSL 파일 생성)"""
    print(f"🔍 prepare_publish_post 호출됨 (post_id: {post_id})")
    
    try:
        # 네이버 블로그 발행기 임포트
        import re
        
        with engine.connect() as conn:
            # 생성된 글 조회
            result = conn.execute(
                text("""
                    SELECT gp.id, gp.title, gp.content, gp.summary, gp.tags
                    FROM generated_posts gp
                    WHERE gp.id = :post_id AND gp.status = 'generated'
                """),
                {"post_id": post_id}
            )
            
            row = result.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="글을 찾을 수 없거나 이미 발행 준비되었습니다")
            
            post_id, title, content, summary, tags_json = row
            
            # 태그 파싱
            import json
            tags = json.loads(tags_json) if tags_json else []
            
            # DSL 태그 제거 함수
            def clean_dsl_tags(text: str) -> str:
                text = re.sub(r'\[title\](.*?)\[/title\]', r'\1', text)
                text = re.sub(r'\[bold\](.*?)\[/bold\]', r'\1', text)
                text = re.sub(r'\[underline\](.*?)\[/underline\]', r'\1', text)
                text = re.sub(r'\[italic\](.*?)\[/italic\]', r'\1', text)
                text = re.sub(r'\[separator=.*?\]\[/separator\]', '', text)
                text = re.sub(r'\[quote=(.*?)\]', r'\1', text)
                text = re.sub(r'\[align=.*?\](.*?)\[/align\]', r'\1', text)
                text = re.sub(r'\[img=.*?\]\[/img\]', '', text)
                return text.strip()
            
            clean_title = clean_dsl_tags(title)
            
            # 발행 상태 업데이트
            conn.execute(
                text("""
                    UPDATE generated_posts 
                    SET status = 'ready_to_publish'
                    WHERE id = :post_id
                """),
                {"post_id": post_id}
            )
            conn.commit()
            
            print(f"✅ 발행 준비 완료: {clean_title}")
            
            return {
                "message": "발행 준비가 완료되었습니다",
                "post_id": post_id,
                "title": clean_title,
                "dsl_content": content,
                "tags": tags,
                "instructions": [
                    "1. 네이버 블로그 접속",
                    "2. 글쓰기 → 스마트에디터",
                    "3. 제목과 본문 입력",
                    "4. 태그 추가",
                    "5. 발행"
                ]
            }
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 발행 준비 실패: {e}")
        raise HTTPException(status_code=500, detail=f"발행 준비 중 오류가 발생했습니다: {str(e)}")

@app.post("/api/generated-posts/{post_id}/mark-published")
async def mark_post_published(
    post_id: int,
    blog_url: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """글을 발행 완료로 표시"""
    print(f"🔍 mark_post_published 호출됨 (post_id: {post_id})")
    
    with engine.connect() as conn:
        conn.execute(
            text("""
                UPDATE generated_posts 
                SET status = 'published', published_at = CURRENT_TIMESTAMP
                WHERE id = :post_id
            """),
            {"post_id": post_id}
        )
        conn.commit()
        
        print(f"✅ 발행 완료 표시: {post_id}")
        
        return {
            "message": "발행 완료로 표시되었습니다",
            "post_id": post_id,
            "blog_url": blog_url
        }

# 애플리케이션 시작/종료 이벤트
@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    print("🚀 스케줄러 시작...")
    scheduler.start()
    
    # 저장된 스케줄 설정 로드
    settings = get_schedule_settings()
    if settings and settings.get('enabled'):
        await update_scheduler(settings)
        print(f"✅ 저장된 스케줄 로드 완료")

@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행"""
    print("🛑 스케줄러 종료...")
    scheduler.shutdown()

if __name__ == "__main__":
    print("🚀 Naver Monitor API 서버 시작 중...")
    print("📋 접속 URL:")
    print("   - API: http://localhost:8001")
    print("   - API Docs: http://localhost:8001/docs")
    print("   - Frontend: http://localhost:3000")
    print("")
    print("🔧 테스트 계정:")
    print("   - 사용자명: testuser")
    print("   - 비밀번호: testpassword123")
    print("")
    print("🔐 로그인 엔드포인트: POST /api/auth/login")
    print("👤 사용자 정보: GET /api/auth/me")
    print("")
    
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)
