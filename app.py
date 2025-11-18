import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# --- 設定 ---
# フォルダID（後で設定画面に入力する値を使う）
FOLDER_ID = st.secrets["FOLDER_ID"]
SCOPES = ['https://www.googleapis.com/auth/drive']

st.set_page_config(page_title="共有ドライブ", page_icon="☁️")
st.title("☁️ ファイル共有サイト")

# --- ログイン機能 ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    pwd = st.text_input("パスワードを入力してください", type="password")
    if st.button("ログイン"):
        # 設定画面のパスワードと一致するか確認
        if pwd == st.secrets["PASSWORD"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("パスワードが違います")
    st.stop()

# --- Google Driveへの接続 ---
try:
    # 設定画面のJSON情報を使って接続
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = service_account.Credentials.from_service_account_info(
        creds_dict, scopes=SCOPES
    )
    service = build('drive', 'v3', credentials=creds)

    # --- 1. アップロード機能 ---
    uploaded_file = st.file_uploader("ファイルをアップロード")
    if uploaded_file:
        file_metadata = {'name': uploaded_file.name, 'parents': [FOLDER_ID]}
        media = MediaIoBaseUpload(uploaded_file, mimetype=uploaded_file.type)
        
        with st.spinner('Google Driveに保存中...'):
            file = service.files().create(
                body=file_metadata, media_body=media, fields='id'
            ).execute()
        st.success(f"保存完了！")

    # --- 2. ファイル一覧と削除 ---
    st.subheader("保存されたファイル")
    
    # ファイルリストを取得
    results = service.files().list(
        q=f"'{FOLDER_ID}' in parents and trashed=false",
        fields="files(id, name)"
    ).execute()
    items = results.get('files', [])

    if not items:
        st.info("ファイルはありません。")
    else:
        for item in items:
            col1, col2 = st.columns([0.8, 0.2])
            col1.text(f"📄 {item['name']}")
            # 削除ボタン
            if col2.button("削除", key=item['id']):
                service.files().delete(fileId=item['id']).execute()
                st.rerun()

except Exception as e:
    st.error(f"設定エラー: {e}")
