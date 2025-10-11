#!/usr/bin/env python3
"""
사용자 비밀번호 업데이트 스크립트
"""
import sys
import os
import bcrypt

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text

# Database setup
DATABASE_URL = "sqlite:///./naver_monitor.db"
engine = create_engine(DATABASE_URL)

def update_user_password():
    """사용자 비밀번호를 간단한 키값으로 업데이트"""
    with engine.connect() as conn:
        # testuser의 비밀번호를 testpassword123으로 설정
        password = "testpassword123"
        
        # 사용자 비밀번호 업데이트
        conn.execute(text("""
            UPDATE users 
            SET hashed_password = :password
            WHERE username = 'testuser'
        """), {"password": password})
        
        conn.commit()
        print(f"✅ 사용자 비밀번호가 업데이트되었습니다.")
        print(f"   사용자명: testuser")
        print(f"   비밀번호: {password}")
        print(f"   저장된 값: {password}")

if __name__ == "__main__":
    print("🔧 사용자 비밀번호 업데이트 중...")
    update_user_password()
    print("🎉 완료!")
