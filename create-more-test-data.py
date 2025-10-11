#!/usr/bin/env python3
"""
더 많은 테스트 데이터 생성 스크립트
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text

# Database setup
DATABASE_URL = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'naver_monitor.db')}"
engine = create_engine(DATABASE_URL)

def create_more_test_data():
    """더 많은 테스트 데이터 생성"""
    with engine.connect() as conn:
        try:
            # 더 많은 키워드 추가
            keywords = [
                ('파이썬', 'Python 프로그래밍 언어'),
                ('자바스크립트', 'JavaScript 웹 개발'),
                ('리액트', 'React 프론트엔드 프레임워크'),
                ('데이터베이스', 'Database 관리 시스템'),
                ('머신러닝', 'Machine Learning AI'),
                ('웹개발', 'Web Development'),
                ('알고리즘', 'Algorithm 문제해결'),
                ('클라우드', 'Cloud Computing'),
                ('Docker', 'Docker 컨테이너'),
                ('Kubernetes', 'K8s 오케스트레이션'),
            ]
            
            for keyword, description in keywords:
                conn.execute(text("""
                    INSERT OR IGNORE INTO keywords (keyword, description, is_active)
                    VALUES (:keyword, :description, 1)
                """), {"keyword": keyword, "description": description})
            
            # 더 많은 블로그 추가
            blogs = [
                ('네이버 블로그', 'blog.naver.com', '네이버 블로그 플랫폼'),
                ('티스토리', 'tistory.com', '티스토리 블로그'),
                ('벨로그', 'velog.io', '개발자 블로그 플랫폼'),
                ('브런치', 'brunch.co.kr', '브런치 글쓰기 플랫폼'),
                ('미디엄', 'medium.com', 'Medium 글로벌 플랫폼'),
                ('개발자 블로그', 'dev.to', '개발자 커뮤니티'),
                ('기술 블로그', 'techcrunch.com', '기술 뉴스'),
                ('스택오버플로우', 'stackoverflow.com', '개발자 Q&A'),
            ]
            
            for name, url_pattern, description in blogs:
                conn.execute(text("""
                    INSERT OR IGNORE INTO blogs (name, url_pattern, description, is_active)
                    VALUES (:name, :url_pattern, :description, 1)
                """), {"name": name, "url_pattern": url_pattern, "description": description})
            
            # 키워드-블로그 타겟 생성 (모든 조합)
            conn.execute(text("""
                INSERT OR IGNORE INTO keyword_targets (keyword_id, blog_id, is_active)
                SELECT k.id, b.id, 1
                FROM keywords k, blogs b
                WHERE k.is_active = 1 AND b.is_active = 1
            """))
            
            # 크롤링 실행 기록 생성
            conn.execute(text("""
                INSERT OR IGNORE INTO crawl_runs (keyword_id, blog_id, status, started_at, completed_at)
                SELECT kt.keyword_id, kt.blog_id, 
                       CASE 
                           WHEN random() % 3 = 0 THEN 'success'
                           WHEN random() % 3 = 1 THEN 'error'
                           ELSE 'pending'
                       END,
                       datetime('now', '-' || (random() % 7) || ' days', '-' || (random() % 24) || ' hours'),
                       CASE 
                           WHEN random() % 3 = 0 THEN datetime('now', '-' || (random() % 7) || ' days', '-' || (random() % 24) || ' hours', '+' || (random() % 60) || ' minutes')
                           ELSE NULL
                       END
                FROM keyword_targets kt
                LIMIT 50
            """))
            
            # 크롤링 결과 생성
            conn.execute(text("""
                INSERT OR IGNORE INTO crawl_results (crawl_run_id, keyword_id, blog_id, rank, title, url, snippet)
                SELECT cr.id, cr.keyword_id, cr.blog_id,
                       (random() % 10) + 1,
                       '테스트 글 제목 ' || cr.id,
                       'https://example.com/post/' || cr.id,
                       '이것은 테스트용 크롤링 결과입니다. 키워드와 관련된 내용이 포함되어 있습니다.'
                FROM crawl_runs cr
                WHERE cr.status = 'success'
                LIMIT 30
            """))
            
            conn.commit()
            print("✅ 더 많은 테스트 데이터가 생성되었습니다!")
            
            # 생성된 데이터 확인
            result = conn.execute(text("SELECT COUNT(*) FROM keywords")).fetchone()
            print(f"   키워드: {result[0]}개")
            
            result = conn.execute(text("SELECT COUNT(*) FROM blogs")).fetchone()
            print(f"   블로그: {result[0]}개")
            
            result = conn.execute(text("SELECT COUNT(*) FROM keyword_targets")).fetchone()
            print(f"   타겟: {result[0]}개")
            
            result = conn.execute(text("SELECT COUNT(*) FROM crawl_runs")).fetchone()
            print(f"   크롤링 실행: {result[0]}개")
            
            result = conn.execute(text("SELECT COUNT(*) FROM crawl_results")).fetchone()
            print(f"   크롤링 결과: {result[0]}개")

        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            conn.rollback()

if __name__ == "__main__":
    print("🔧 더 많은 테스트 데이터 생성 중...")
    create_more_test_data()
    print("🎉 완료!")

