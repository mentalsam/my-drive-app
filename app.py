import streamlit as st
import requests
import base64

# ▼▼▼ ここにさっきコピーしたURLを貼り付けてください！ ▼▼▼
# 例: "https://script.google.com/macros/s/...../exec"
GAS_URL = "https://script.google.com/macros/s/AKfycbywoFnLCLr03K6Qmk35ogwcV5ZUu2Lz_Hz3_y8f7-cS92C3nBvZJsGqdM5qvj1IPnKg/exec"

st.set_page_config(page_title="共有ドライブ", page_icon="📂")
st.title("📂 ファイル共有サイト")

# --- ログイン機能 ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    pwd = st.text_input("パスワード", type="password")
    if st.button("ログイン"):
        # SecretsのPASSWORDと一致するか確認
        if pwd == st.secrets["PASSWORD"]:
            st.session_state.authenticated = True
            st.rerun()
    st.stop()

# --- メイン画面 ---
with st.expander("📤 ファイルをアップロード", expanded=True):
    uploaded_file = st.file_uploader("ファイルを選択")
    if uploaded_file and st.button("アップロード実行"):
        with st.spinner("送信中..."):
            try:
                file_bytes = uploaded_file.read()
                file_b64 = base64.b64encode(file_bytes).decode('utf-8')
                
                # GASへ送信
                response = requests.post(GAS_URL, json={
                    "action": "upload",
                    "name": uploaded_file.name,
                    "mimeType": uploaded_file.type,
                    "file": file_b64
                })
                
                if response.status_code == 200:
                    st.success("保存しました！")
                    st.rerun()
                else:
                    st.error("送信エラーが発生しました")
            except Exception as e:
                st.error(f"エラー: {e}")

st.divider()
st.subheader("保存されたファイル")

# 一覧取得
try:
    resp = requests.post(GAS_URL, json={"action": "list"})
    files = resp.json().get("files", [])
except:
    files = []

if not files:
    st.info("ファイルはありません")
else:
    # ダウンロード機能
    file_map = {f['name']: f['id'] for f in files}
    selected = st.selectbox("ダウンロードするファイルを選択", file_map.keys())
    
    if st.button("ダウンロード準備"):
        with st.spinner("準備中..."):
            r = requests.post(GAS_URL, json={"action": "download", "id": file_map[selected]})
            d = r.json()
            if "data" in d:
                st.download_button("💾 保存する", base64.b64decode(d['data']), d['name'])
            else:
                st.error("ダウンロードに失敗しました")

    st.divider()
    
    # 削除リスト
    for f in files:
        c1, c2 = st.columns([0.8, 0.2])
        c1.text(f.get('name'))
        if c2.button("削除", key=f['id']):
            requests.post(GAS_URL, json={"action": "delete", "id": f['id']})
            st.rerun()
