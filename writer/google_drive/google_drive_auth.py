# google_drive_auth.py
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os

# 사용할 권한 범위 설정 (여기선 Drive 읽기 전용)
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def authenticate():
    creds = None
    if os.path.exists('../common/token.json'):
        creds = Credentials.from_authorized_user_file('../common/token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # 이 부분에서 브라우저가 열리며 로그인 요청
            flow = InstalledAppFlow.from_client_secrets_file('../common/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # 로그인 성공 시 token.json 생성
        with open('../common/token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

# 단독 실행 테스트
if __name__ == "__main__":
    authenticate()