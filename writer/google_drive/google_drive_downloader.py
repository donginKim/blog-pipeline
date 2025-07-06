import os
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# Google Drive API 사용 범위
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def authenticate():
    creds = None
    if os.path.exists('common/token.json'):
        creds = Credentials.from_authorized_user_file('common/token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('common/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('common/token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

def find_folder_id_by_name(service, parent_id, folder_name):
    """부모 폴더(parent_id) 하위에서 특정 이름의 폴더 ID를 찾는다"""
    query = f"'{parent_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and name = '{folder_name}' and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    folders = results.get('files', [])
    return folders[0]['id'] if folders else None

def list_images_in_folder(service, folder_id):
    query = f"'{folder_id}' in parents and mimeType contains 'image/' and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    return results.get('files', [])

def download_file(service, file_id, file_name, access_token, save_dir="temp"):
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, file_name)
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f"[✓] Downloaded: {file_name}")
    else:
        print(f"[!] Failed to download {file_name}: {response.status_code}")

def download_today_images():
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    today_str = datetime.now().strftime("%Y%m%d")

    try:
        # 1. 'img-data' 폴더 ID 조회 (최상위에 있어야 함)
        img_data_folder_id = find_folder_id_by_name(service, parent_id='root', folder_name='img-data')
        if not img_data_folder_id:
            print("[!] 'img-data' 폴더를 찾을 수 없습니다.")
            return

        # 2. 'img-data/YYYYMMDD' 폴더 ID 조회
        target_folder_id = find_folder_id_by_name(service, parent_id=img_data_folder_id, folder_name=today_str)
        if not target_folder_id:
            print(f"[!] '{today_str}' 폴더를 찾을 수 없습니다.")
            return

        # 3. 이미지 목록 조회
        image_files = list_images_in_folder(service, target_folder_id)
        if not image_files:
            print(f"[!] 이미지가 없습니다: {today_str}")
            return

        # 4. 파일 다운로드
        for file in image_files:
            download_file(service, file['id'], file['name'], creds.token)

    except HttpError as error:
        print(f"[!] Google Drive API 오류: {error}")

# 단독 실행 테스트용
if __name__ == "__main__":
    download_today_images()