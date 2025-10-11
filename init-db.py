#!/usr/bin/env python3
"""
간단한 데이터베이스 초기화 스크립트
"""
import asyncio
import sys
import os
import hashlib
import bcrypt

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Database setup
DATABASE_URL = "sqlite:///./naver_monitor.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Create tables
def create_tables():
    """테이블 생성"""
    with engine.connect() as conn:
        # Users table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR(255) UNIQUE NOT NULL,
                username VARCHAR(100) UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Keywords table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword VARCHAR(255) NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Blogs table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS blogs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) NOT NULL,
                url_pattern VARCHAR(500) NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Keyword targets table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS keyword_targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword_id INTEGER NOT NULL,
                blog_id INTEGER NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (keyword_id) REFERENCES keywords (id),
                FOREIGN KEY (blog_id) REFERENCES blogs (id),
                UNIQUE(keyword_id, blog_id)
            )
        """))
        
        # Crawl runs table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS crawl_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword_id INTEGER NOT NULL,
                blog_id INTEGER NOT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                started_at DATETIME,
                completed_at DATETIME,
                error_message TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (keyword_id) REFERENCES keywords (id),
                FOREIGN KEY (blog_id) REFERENCES blogs (id)
            )
        """))
        
        # Crawl results table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS crawl_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                crawl_run_id INTEGER NOT NULL,
                keyword_id INTEGER NOT NULL,
                blog_id INTEGER NOT NULL,
                rank INTEGER,
                title TEXT,
                url TEXT,
                snippet TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (crawl_run_id) REFERENCES crawl_runs (id),
                FOREIGN KEY (keyword_id) REFERENCES keywords (id),
                FOREIGN KEY (blog_id) REFERENCES blogs (id)
            )
        """))
        conn.commit()


def create_test_data():
    """테스트 데이터 생성"""
    with engine.connect() as conn:
        try:
            # Create test user
            password = "testpassword123"
            conn.execute(text("""
                INSERT OR IGNORE INTO users (email, username, hashed_password, is_active)
                VALUES ('test@example.com', 'testuser', :password, 1)
            """), {"password": password})
            
            # Create test keywords
            keywords = [
                ('파이썬', 'Python 프로그래밍'),
                ('자바스크립트', 'JavaScript 개발'),
                ('리액트', 'React 프론트엔드'),
                ('데이터베이스', 'Database 관련'),
            ]
            
            for keyword, description in keywords:
                conn.execute(text("""
                    INSERT OR IGNORE INTO keywords (keyword, description, is_active)
                    VALUES (:keyword, :description, 1)
                """), {"keyword": keyword, "description": description})
            
            # Create test blogs
            blogs = [
                ('내 블로그', 'https://blog.naver.com/myblog', '개인 블로그'),
                ('기술 블로그', 'https://blog.naver.com/techblog', '기술 관련 블로그'),
                ('일상 블로그', 'https://blog.naver.com/dailyblog', '일상 기록 블로그'),
            ]
            
            for name, url_pattern, description in blogs:
                conn.execute(text("""
                    INSERT OR IGNORE INTO blogs (name, url_pattern, description, is_active)
                    VALUES (:name, :url_pattern, :description, 1)
                """), {"name": name, "url_pattern": url_pattern, "description": description})
            
            # Create test targets
            targets = [
                (1, 1),  # 파이썬 -> 내 블로그
                (2, 1),  # 자바스크립트 -> 내 블로그
                (3, 2),  # 리액트 -> 기술 블로그
                (4, 2),  # 데이터베이스 -> 기술 블로그
                (1, 3),  # 파이썬 -> 일상 블로그
            ]
            
            for keyword_id, blog_id in targets:
                conn.execute(text("""
                    INSERT OR IGNORE INTO keyword_targets (keyword_id, blog_id, is_active)
                    VALUES (:keyword_id, :blog_id, 1)
                """), {"keyword_id": keyword_id, "blog_id": blog_id})
            
            conn.commit()
            print("✅ 테스트 데이터가 생성되었습니다!")
            
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            conn.rollback()


if __name__ == "__main__":
    print("🔧 데이터베이스 초기화 중...")
    create_tables()
    print("✅ 테이블이 생성되었습니다!")
    
    print("📊 테스트 데이터 생성 중...")
    create_test_data()
    
    print("🎉 완료!")
