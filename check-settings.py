#!/usr/bin/env python3
"""
설정 확인 스크립트
"""
import sys
import os
import json

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text

# Database setup
DATABASE_URL = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'naver_monitor.db')}"
engine = create_engine(DATABASE_URL)

def check_settings():
    """설정 확인"""
    with engine.connect() as conn:
        print("📋 현재 설정 확인")
        print("=" * 60)
        
        # 모든 설정 조회
        result = conn.execute(text("SELECT key, value, updated_at FROM settings"))
        settings = result.fetchall()
        
        for key, value, updated_at in settings:
            print(f"\n🔧 {key}:")
            print(f"   업데이트: {updated_at}")
            
            # JSON 파싱하여 보기 좋게 출력
            try:
                parsed = json.loads(value)
                print(f"   내용:")
                for k, v in parsed.items():
                    print(f"      - {k}: {v}")
            except:
                print(f"   내용: {value}")
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    check_settings()


