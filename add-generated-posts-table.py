#!/usr/bin/env python3
"""
생성된 블로그 글 저장 테이블 추가
"""
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text

# Database setup
DATABASE_URL = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'naver_monitor.db')}"
engine = create_engine(DATABASE_URL)

def add_generated_posts_table():
    """생성된 글 테이블 추가"""
    with engine.connect() as conn:
        try:
            print("📋 생성된 블로그 글 테이블 추가 중...")
            
            # generated_posts 테이블 생성
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS generated_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    keyword_id INTEGER,
                    crawl_run_id INTEGER,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    summary TEXT,
                    tags TEXT,
                    status TEXT DEFAULT 'generated',
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    published_at TIMESTAMP,
                    FOREIGN KEY (keyword_id) REFERENCES keywords(id),
                    FOREIGN KEY (crawl_run_id) REFERENCES crawl_runs(id)
                )
            """))
            
            conn.commit()
            print("✅ 생성된 블로그 글 테이블 추가 완료!")
            
            # 인덱스 추가
            print("📊 인덱스 추가 중...")
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_generated_posts_keyword_id 
                ON generated_posts(keyword_id)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_generated_posts_status 
                ON generated_posts(status)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_generated_posts_created_at 
                ON generated_posts(created_at)
            """))
            
            conn.commit()
            print("✅ 인덱스 추가 완료!")
            
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            conn.rollback()

if __name__ == "__main__":
    add_generated_posts_table()
    print("🎉 완료!")

