#!/usr/bin/env python3
"""
테스트용 사용자 생성 스크립트
"""
import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.database import AsyncSessionLocal
from app.services.user_service import UserService
from app.schemas import UserCreate


async def create_test_user():
    """테스트용 사용자 생성"""
    async with AsyncSessionLocal() as db:
        user_service = UserService(db)
        
        # Check if user already exists
        existing_user = await user_service.get_by_username("testuser")
        if existing_user:
            print("✅ 테스트 사용자가 이미 존재합니다.")
            print(f"   사용자명: {existing_user.username}")
            print(f"   이메일: {existing_user.email}")
            return
        
        # Create test user
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="testpassword123"
        )
        
        user = await user_service.create_user(user_data)
        print("✅ 테스트 사용자가 생성되었습니다!")
        print(f"   사용자명: {user.username}")
        print(f"   이메일: {user.email}")
        print(f"   비밀번호: testpassword123")


if __name__ == "__main__":
    print("🔧 테스트 사용자 생성 중...")
    asyncio.run(create_test_user())
    print("🎉 완료!")

