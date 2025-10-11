#!/usr/bin/env python3
"""
설정 테이블 추가 스크립트
"""
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text

# Database setup
DATABASE_URL = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'naver_monitor.db')}"
engine = create_engine(DATABASE_URL)

def add_settings_table():
    """설정 테이블 추가"""
    with engine.connect() as conn:
        try:
            print("📋 설정 테이블 생성 중...")
            
            # settings 테이블 생성
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL UNIQUE,
                    value TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            conn.commit()
            print("✅ 설정 테이블 생성 완료!")
            
            # 기본 설정 추가
            print("📝 기본 설정 추가 중...")
            
            # 알림 설정 기본값
            conn.execute(text("""
                INSERT OR IGNORE INTO settings (key, value) 
                VALUES ('notification_settings', '{"enabled": false, "phone": "", "notify_on_success": true, "notify_on_error": true}')
            """))
            
            # 스케줄 설정 기본값
            conn.execute(text("""
                INSERT OR IGNORE INTO settings (key, value) 
                VALUES ('schedule_settings', '{"enabled": false, "time": "09:00", "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]}')
            """))
            
            # AI 블로그 설정 기본값
            conn.execute(text("""
                INSERT OR IGNORE INTO settings (key, value) 
                VALUES ('ai_blog_settings', '{"enabled": false, "use_openai": false, "model": "gpt-3.5-turbo", "temperature": 0.7}')
            """))
            
            conn.commit()
            print("✅ 기본 설정 추가 완료!")
            
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            conn.rollback()

if __name__ == "__main__":
    add_settings_table()
    print("🎉 완료!")


