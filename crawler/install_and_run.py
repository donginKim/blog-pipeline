import subprocess
import sys

def install_requirements():
    try:
        import playwright
    except ImportError:
        print("📦 필요한 라이브러리를 설치 중입니다...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 설치 완료!")

        # Playwright 설치 (브라우저 다운로드 포함)
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])

def main():
    from modules.main import run
    run()

if __name__ == "__main__":
    install_requirements()
    main()
