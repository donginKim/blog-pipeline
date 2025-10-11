#!/usr/bin/env python3
"""
테스트용 샘플 데이터 생성 스크립트
"""
import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.database import AsyncSessionLocal
from app.services.keyword_service import KeywordService
from app.services.blog_service import BlogService
from app.services.target_service import TargetService
from app.schemas import KeywordCreate, BlogCreate, KeywordTargetCreate


async def create_test_data():
    """테스트용 샘플 데이터 생성"""
    async with AsyncSessionLocal() as db:
        keyword_service = KeywordService(db)
        blog_service = BlogService(db)
        target_service = TargetService(db)
        
        print("🔧 테스트 데이터 생성 중...")
        
        # Create keywords
        keywords_data = [
            KeywordCreate(keyword="파이썬", description="Python 프로그래밍"),
            KeywordCreate(keyword="자바스크립트", description="JavaScript 개발"),
            KeywordCreate(keyword="리액트", description="React 프론트엔드"),
            KeywordCreate(keyword="데이터베이스", description="Database 관련"),
        ]
        
        keywords = []
        for kw_data in keywords_data:
            existing = await keyword_service.get_by_keyword(kw_data.keyword)
            if existing:
                keywords.append(existing)
                print(f"   키워드 '{kw_data.keyword}' 이미 존재")
            else:
                keyword = await keyword_service.create_keyword(kw_data)
                keywords.append(keyword)
                print(f"   키워드 '{kw_data.keyword}' 생성")
        
        # Create blogs
        blogs_data = [
            BlogCreate(name="내 블로그", url_pattern="https://blog.naver.com/myblog", description="개인 블로그"),
            BlogCreate(name="기술 블로그", url_pattern="https://blog.naver.com/techblog", description="기술 관련 블로그"),
            BlogCreate(name="일상 블로그", url_pattern="https://blog.naver.com/dailyblog", description="일상 기록 블로그"),
        ]
        
        blogs = []
        for blog_data in blogs_data:
            existing = await blog_service.get_by_url_pattern(blog_data.url_pattern)
            if existing:
                blogs.append(existing)
                print(f"   블로그 '{blog_data.name}' 이미 존재")
            else:
                blog = await blog_service.create_blog(blog_data)
                blogs.append(blog)
                print(f"   블로그 '{blog_data.name}' 생성")
        
        # Create targets
        targets_data = [
            KeywordTargetCreate(keyword_id=keywords[0].id, blog_id=blogs[0].id),
            KeywordTargetCreate(keyword_id=keywords[1].id, blog_id=blogs[0].id),
            KeywordTargetCreate(keyword_id=keywords[2].id, blog_id=blogs[1].id),
            KeywordTargetCreate(keyword_id=keywords[3].id, blog_id=blogs[1].id),
            KeywordTargetCreate(keyword_id=keywords[0].id, blog_id=blogs[2].id),
        ]
        
        for target_data in targets_data:
            existing = await target_service.get_by_keyword_and_blog(target_data.keyword_id, target_data.blog_id)
            if existing:
                print(f"   타겟 '{keywords[target_data.keyword_id-1].keyword}' → '{blogs[target_data.blog_id-1].name}' 이미 존재")
            else:
                await target_service.create_target(target_data)
                print(f"   타겟 '{keywords[target_data.keyword_id-1].keyword}' → '{blogs[target_data.blog_id-1].name}' 생성")
        
        print("✅ 테스트 데이터 생성 완료!")


if __name__ == "__main__":
    asyncio.run(create_test_data())
    print("🎉 완료!")

