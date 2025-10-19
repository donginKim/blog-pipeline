#!/usr/bin/env python3
"""
PostgreSQL 데이터베이스 초기화 스크립트
"""
import os
import sys
from sqlalchemy import create_engine, text

# 환경 변수에서 DATABASE_URL 가져오기
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://naver_monitor:changeme@db:5432/naver_monitor"
)

print(f"🔍 데이터베이스: {DATABASE_URL}")

try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    
    with engine.connect() as conn:
        print("✅ 데이터베이스 연결 성공")
        
        # 테이블 생성
        print("📝 테이블 생성 중...")
        
        # Users table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Keywords table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS keywords (
                id SERIAL PRIMARY KEY,
                keyword VARCHAR(255) NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Blogs table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS blogs (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                url_pattern VARCHAR(500) NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Keyword_targets table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS keyword_targets (
                id SERIAL PRIMARY KEY,
                keyword_id INTEGER REFERENCES keywords(id) ON DELETE CASCADE,
                blog_id INTEGER REFERENCES blogs(id) ON DELETE CASCADE,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(keyword_id, blog_id)
            )
        """))
        
        # Crawl_runs table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS crawl_runs (
                id SERIAL PRIMARY KEY,
                keyword VARCHAR(255),
                blog_name VARCHAR(255),
                status VARCHAR(50) DEFAULT 'running',
                error_message TEXT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Crawl_results table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS crawl_results (
                id SERIAL PRIMARY KEY,
                crawl_run_id INTEGER REFERENCES crawl_runs(id) ON DELETE CASCADE,
                keyword VARCHAR(255) NOT NULL,
                blog_name VARCHAR(255) NOT NULL,
                rank INTEGER NOT NULL,
                title TEXT NOT NULL,
                url VARCHAR(1000) NOT NULL,
                snippet TEXT,
                section VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Settings table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS settings (
                id SERIAL PRIMARY KEY,
                key VARCHAR(255) UNIQUE NOT NULL,
                value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Generated_posts table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS generated_posts (
                id SERIAL PRIMARY KEY,
                keyword_id INTEGER REFERENCES keywords(id) ON DELETE CASCADE,
                target_id INTEGER REFERENCES keyword_targets(id) ON DELETE SET NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                summary TEXT,
                tags TEXT,
                status VARCHAR(50) DEFAULT 'draft',
                naver_post_id VARCHAR(255),
                published_url VARCHAR(1000),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                published_at TIMESTAMP
            )
        """))
        
        conn.commit()
        print("✅ 테이블 생성 완료")
        
        # 테스트 사용자 생성
        print("👤 테스트 사용자 생성...")
        result = conn.execute(text("SELECT COUNT(*) FROM users WHERE username = 'testuser'"))
        count = result.fetchone()[0]
        
        if count == 0:
            conn.execute(text("""
                INSERT INTO users (username, email, hashed_password, is_active)
                VALUES ('testuser', 'test@example.com', 'testpassword123', TRUE)
            """))
            conn.commit()
            print("✅ 테스트 사용자 생성 완료 (testuser / testpassword123)")
        else:
            print("⚠️  테스트 사용자가 이미 존재합니다")
        
        print("")
        print("========================================")
        print("✅ 데이터베이스 초기화 완료!")
        print("========================================")
        print("")
        print("📋 접속 정보:")
        print("   사용자명: testuser")
        print("   비밀번호: testpassword123")
        print("")
        print("⚠️  비밀번호를 변경하세요:")
        print("   docker exec -it naver-monitor-backend python3 change-password.py")
        print("")

except Exception as e:
    print(f"❌ 오류 발생: {e}")
    sys.exit(1)

