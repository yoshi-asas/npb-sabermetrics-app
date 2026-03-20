import streamlit as st

def check_password():
    """入力されたパスワードが正しいかチェックします"""
    
    if "password" not in st.secrets:
        st.error("⚠️ 致命的エラー: `st.secrets` にパスワードが設定されていません。Streamlit Cloudのダッシュボードで設定してください。")
        st.stop()
        
    CORRECT_PASSWORD = st.secrets["password"]
    
    def password_entered():
        """入力されたパスワードと一致するか判定"""
        if st.session_state["password_input"] == CORRECT_PASSWORD:
            st.session_state["password_correct"] = True
            del st.session_state["password_input"] # 安全のためセッションから値は消去
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # 初回アクセス時：パスワード入力欄を表示
        st.title("🔒 パスワード保護されています")
        st.info("このアプリを閲覧するにはパスワードを入力し、Enterキーを押してください。")
        st.text_input(
            "閲覧パスワード:", 
            type="password", 
            on_change=password_entered, 
            key="password_input"
        )
        return False
    
    elif not st.session_state["password_correct"]:
        # パスワードが間違っている場合
        st.title("🔒 パスワード保護されています")
        st.text_input(
            "閲覧パスワード:", 
            type="password", 
            on_change=password_entered, 
            key="password_input"
        )
        st.error("❌ パスワードが間違っています。もう一度お試しください。")
        return False
        
    else:
        # パスワード正解時
        return True
