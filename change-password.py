#!/usr/bin/env python3
"""
간단한 비밀번호 변경 스크립트
가상환경 없이도 작동 (sqlite3만 사용)
"""
import sqlite3
import getpass
import sys
import os

def main():
    print("=" * 60)
    print("🔒 Naver Monitor - 비밀번호 변경")
    print("=" * 60)
    print()
    
    # 데이터베이스 확인
    db_path = os.path.join(os.path.dirname(__file__), 'naver_monitor.db')
    if not os.path.exists(db_path):
        print("❌ 데이터베이스를 찾을 수 없습니다:", db_path)
        sys.exit(1)
    
    # 데이터베이스 연결
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 현재 사용자 목록
    print("📋 현재 등록된 사용자:")
    print("-" * 60)
    cursor.execute("SELECT id, username, email, is_active FROM users")
    users = cursor.fetchall()
    
    if not users:
        print("❌ 등록된 사용자가 없습니다.")
        conn.close()
        sys.exit(1)
    
    for user_id, username, email, is_active in users:
        status = "✅ 활성" if is_active else "❌ 비활성"
        print(f"  ID: {user_id:3d} | {username:15s} | {email:25s} | {status}")
    print("-" * 60)
    print()
    
    # 사용자 선택
    try:
        user_id = int(input("사용자 ID: ").strip())
    except ValueError:
        print("❌ 올바른 숫자를 입력하세요.")
        conn.close()
        sys.exit(1)
    
    # 사용자 확인
    cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    
    if not result:
        print(f"❌ 사용자 ID {user_id}를 찾을 수 없습니다.")
        conn.close()
        sys.exit(1)
    
    username = result[0]
    print(f"선택한 사용자: {username}")
    print()
    
    # 새 비밀번호 입력
    new_password = getpass.getpass("새 비밀번호: ").strip()
    
    if not new_password:
        print("❌ 비밀번호는 비어있을 수 없습니다.")
        conn.close()
        sys.exit(1)
    
    # 비밀번호 확인
    confirm_password = getpass.getpass("비밀번호 확인: ").strip()
    
    if new_password != confirm_password:
        print("❌ 비밀번호가 일치하지 않습니다.")
        conn.close()
        sys.exit(1)
    
    # 비밀번호 업데이트
    cursor.execute(
        "UPDATE users SET hashed_password = ? WHERE id = ?",
        (new_password, user_id)
    )
    conn.commit()
    
    print()
    print("✅ 비밀번호가 변경되었습니다!")
    print()
    print("📋 새 로그인 정보:")
    print(f"   사용자명: {username}")
    print(f"   비밀번호: {new_password}")
    print()
    print("⚠️  새 비밀번호를 기억해두세요!")
    print()
    
    conn.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 취소되었습니다.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        sys.exit(1)

