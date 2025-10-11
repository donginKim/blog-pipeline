#!/usr/bin/env python3
"""
데이터베이스 테스트 데이터 정리 스크립트
사용자 계정은 유지하고, 키워드/블로그/타겟/크롤링 데이터만 삭제
"""
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text

# Database setup
DATABASE_URL = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'naver_monitor.db')}"
engine = create_engine(DATABASE_URL)

def clean_test_data():
    """테스트 데이터 정리 (사용자는 유지)"""
    with engine.connect() as conn:
        try:
            print("🧹 테스트 데이터 정리 중...")
            
            # 크롤링 결과 삭제
            result = conn.execute(text("DELETE FROM crawl_results"))
            print(f"   - 크롤링 결과 삭제: {result.rowcount}개")
            
            # 크롤링 실행 기록 삭제
            result = conn.execute(text("DELETE FROM crawl_runs"))
            print(f"   - 크롤링 실행 기록 삭제: {result.rowcount}개")
            
            # 타겟 삭제
            result = conn.execute(text("DELETE FROM keyword_targets"))
            print(f"   - 타겟 삭제: {result.rowcount}개")
            
            # 블로그 삭제
            result = conn.execute(text("DELETE FROM blogs"))
            print(f"   - 블로그 삭제: {result.rowcount}개")
            
            # 키워드 삭제
            result = conn.execute(text("DELETE FROM keywords"))
            print(f"   - 키워드 삭제: {result.rowcount}개")
            
            conn.commit()
            print("✅ 테스트 데이터 정리 완료!")
            print("")
            print("📊 남은 데이터:")
            
            # 사용자 확인
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.fetchone()[0]
            print(f"   - 사용자: {user_count}개")
            
            # 모든 테이블 확인
            result = conn.execute(text("SELECT COUNT(*) FROM keywords"))
            print(f"   - 키워드: {result.fetchone()[0]}개")
            
            result = conn.execute(text("SELECT COUNT(*) FROM blogs"))
            print(f"   - 블로그: {result.fetchone()[0]}개")
            
            result = conn.execute(text("SELECT COUNT(*) FROM keyword_targets"))
            print(f"   - 타겟: {result.fetchone()[0]}개")
            
            result = conn.execute(text("SELECT COUNT(*) FROM crawl_runs"))
            print(f"   - 크롤링 실행: {result.fetchone()[0]}개")
            
            result = conn.execute(text("SELECT COUNT(*) FROM crawl_results"))
            print(f"   - 크롤링 결과: {result.fetchone()[0]}개")

        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            conn.rollback()

if __name__ == "__main__":
    print("⚠️  주의: 이 스크립트는 모든 테스트 데이터를 삭제합니다!")
    print("   (사용자 계정은 유지됩니다)")
    print("")
    
    confirm = input("계속하시겠습니까? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ 취소되었습니다.")
        sys.exit(0)
    
    print("")
    clean_test_data()
    print("")
    print("🎉 완료!")


