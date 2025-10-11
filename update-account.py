#!/usr/bin/env python3
"""
계정 정보 수정 스크립트
"""
import sys
import os
import getpass

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text

# Database setup
DATABASE_URL = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'naver_monitor.db')}"
engine = create_engine(DATABASE_URL)

def list_users():
    """현재 등록된 사용자 목록"""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, username, email, is_active FROM users"))
        users = result.fetchall()
        
        if not users:
            print("❌ 등록된 사용자가 없습니다.")
            return []
        
        print("\n📋 현재 등록된 사용자:")
        print("-" * 60)
        for user_id, username, email, is_active in users:
            status = "✅ 활성" if is_active else "❌ 비활성"
            print(f"  ID: {user_id} | {username} | {email} | {status}")
        print("-" * 60)
        
        return users

def update_username(user_id: int):
    """사용자명 변경"""
    new_username = input("\n새 사용자명: ").strip()
    
    if not new_username:
        print("❌ 사용자명은 비어있을 수 없습니다.")
        return False
    
    with engine.connect() as conn:
        # 중복 확인
        result = conn.execute(text("SELECT id FROM users WHERE username = :username AND id != :user_id"), 
                            {"username": new_username, "user_id": user_id})
        if result.fetchone():
            print(f"❌ '{new_username}'은 이미 사용 중인 사용자명입니다.")
            return False
        
        conn.execute(text("UPDATE users SET username = :username WHERE id = :user_id"),
                    {"username": new_username, "user_id": user_id})
        conn.commit()
        print(f"✅ 사용자명이 '{new_username}'으로 변경되었습니다.")
        return True

def update_email(user_id: int):
    """이메일 변경"""
    new_email = input("\n새 이메일: ").strip()
    
    if not new_email:
        print("❌ 이메일은 비어있을 수 없습니다.")
        return False
    
    with engine.connect() as conn:
        conn.execute(text("UPDATE users SET email = :email WHERE id = :user_id"),
                    {"email": new_email, "user_id": user_id})
        conn.commit()
        print(f"✅ 이메일이 '{new_email}'로 변경되었습니다.")
        return True

def update_password(user_id: int):
    """비밀번호 변경"""
    new_password = getpass.getpass("\n새 비밀번호: ").strip()
    
    if not new_password:
        print("❌ 비밀번호는 비어있을 수 없습니다.")
        return False
    
    confirm_password = getpass.getpass("비밀번호 확인: ").strip()
    
    if new_password != confirm_password:
        print("❌ 비밀번호가 일치하지 않습니다.")
        return False
    
    with engine.connect() as conn:
        conn.execute(text("UPDATE users SET hashed_password = :password WHERE id = :user_id"),
                    {"password": new_password, "user_id": user_id})
        conn.commit()
        print(f"✅ 비밀번호가 변경되었습니다.")
        return True

def toggle_active(user_id: int):
    """계정 활성화/비활성화 토글"""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT is_active FROM users WHERE id = :user_id"),
                            {"user_id": user_id})
        current_active = result.fetchone()[0]
        new_active = 0 if current_active else 1
        
        conn.execute(text("UPDATE users SET is_active = :is_active WHERE id = :user_id"),
                    {"is_active": new_active, "user_id": user_id})
        conn.commit()
        
        status = "활성화" if new_active else "비활성화"
        print(f"✅ 계정이 {status}되었습니다.")
        return True

def create_user():
    """새 사용자 생성"""
    print("\n🆕 새 사용자 생성")
    print("-" * 60)
    
    username = input("사용자명: ").strip()
    if not username:
        print("❌ 사용자명은 필수입니다.")
        return False
    
    email = input("이메일: ").strip()
    if not email:
        print("❌ 이메일은 필수입니다.")
        return False
    
    password = getpass.getpass("비밀번호: ").strip()
    if not password:
        print("❌ 비밀번호는 필수입니다.")
        return False
    
    confirm_password = getpass.getpass("비밀번호 확인: ").strip()
    if password != confirm_password:
        print("❌ 비밀번호가 일치하지 않습니다.")
        return False
    
    with engine.connect() as conn:
        # 중복 확인
        result = conn.execute(text("SELECT id FROM users WHERE username = :username"),
                            {"username": username})
        if result.fetchone():
            print(f"❌ '{username}'은 이미 사용 중인 사용자명입니다.")
            return False
        
        conn.execute(text("""
            INSERT INTO users (username, email, hashed_password, is_active)
            VALUES (:username, :email, :password, 1)
        """), {"username": username, "email": email, "password": password})
        conn.commit()
        print(f"✅ 사용자 '{username}'이 생성되었습니다.")
        return True

def delete_user(user_id: int):
    """사용자 삭제"""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT username FROM users WHERE id = :user_id"),
                            {"user_id": user_id})
        username = result.fetchone()[0]
        
        confirm = input(f"\n⚠️  정말로 사용자 '{username}'을 삭제하시겠습니까? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ 취소되었습니다.")
            return False
        
        conn.execute(text("DELETE FROM users WHERE id = :user_id"),
                    {"user_id": user_id})
        conn.commit()
        print(f"✅ 사용자 '{username}'이 삭제되었습니다.")
        return True

def main():
    print("=" * 60)
    print("🔧 Naver Monitor - 계정 관리")
    print("=" * 60)
    
    while True:
        users = list_users()
        
        print("\n📝 작업 선택:")
        print("  1. 사용자명 변경")
        print("  2. 이메일 변경")
        print("  3. 비밀번호 변경")
        print("  4. 계정 활성화/비활성화")
        print("  5. 새 사용자 생성")
        print("  6. 사용자 삭제")
        print("  0. 종료")
        
        choice = input("\n선택 (0-6): ").strip()
        
        if choice == '0':
            print("\n👋 종료합니다.")
            break
        
        if choice == '5':
            create_user()
            continue
        
        if choice in ['1', '2', '3', '4', '6']:
            if not users:
                print("❌ 수정할 사용자가 없습니다.")
                continue
            
            user_id = input("\n사용자 ID: ").strip()
            if not user_id.isdigit():
                print("❌ 올바른 사용자 ID를 입력하세요.")
                continue
            
            user_id = int(user_id)
            if not any(u[0] == user_id for u in users):
                print("❌ 존재하지 않는 사용자 ID입니다.")
                continue
            
            if choice == '1':
                update_username(user_id)
            elif choice == '2':
                update_email(user_id)
            elif choice == '3':
                update_password(user_id)
            elif choice == '4':
                toggle_active(user_id)
            elif choice == '6':
                delete_user(user_id)
        else:
            print("❌ 올바른 선택이 아닙니다.")
        
        input("\n⏎ 계속하려면 Enter를 누르세요...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 종료합니다.")
        sys.exit(0)


