#!/usr/bin/env python3
"""
로그인 디버깅 스크립트
"""
import sys
import os
import hashlib

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text

# Database setup
DATABASE_URL = "sqlite:///./naver_monitor.db"
engine = create_engine(DATABASE_URL)

def debug_login(username: str, password: str):
    """로그인 디버깅"""
    print(f"=== 로그인 디버깅: {username} ===")
    
    with engine.connect() as conn:
        # 1. 사용자 조회
        result = conn.execute(text("""
            SELECT id, username, email, hashed_password, is_active
            FROM users
            WHERE username = :username AND is_active = 1
        """), {"username": username})
        
        user = result.fetchone()
        print(f"1. 사용자 조회 결과: {user}")
        
        if not user:
            print("❌ 사용자를 찾을 수 없습니다.")
            return False
        
        # 2. 비밀번호 해시 비교
        stored_password = user[3]
        input_hash = hashlib.sha256(password.encode()).hexdigest()
        
        print(f"2. 저장된 해시: {stored_password}")
        print(f"3. 입력 해시:   {input_hash}")
        print(f"4. 해시 일치:   {stored_password == input_hash}")
        
        if stored_password == input_hash:
            print("✅ 로그인 성공!")
            return True
        else:
            print("❌ 비밀번호가 일치하지 않습니다.")
            return False

if __name__ == "__main__":
    print("🔍 로그인 디버깅 시작...")
    success = debug_login("testuser", "testpassword123")
    print(f"결과: {'성공' if success else '실패'}")

