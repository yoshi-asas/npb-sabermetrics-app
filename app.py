import streamlit as st
import pandas as pd

st.set_page_config(page_title="プロ野球選手 セイバーメトリクス一覧", layout="wide")

# --- 🔒 パスワード保護（Basic Auth風） ---
def check_password():
    """入力されたパスワードが正しいかチェックします"""
    
    # 🌟 Streamlit公式の安全なSecrets機能からパスワードを取得します
    # ※設定漏れエラーを防ぐため、取得できない時はアプリを停止させます
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

# パスワードチェックに通過しない場合は下のメイン画面のコードの実行をストップ（画面を隠す）
if not check_password():
    st.stop()
# ---------------------------------

st.title("⚾ プロ野球選手 セイバーメトリクス一覧")
st.markdown("選手の成績（打数、安打など）が入ったCSVファイルを読み込んで、**wOBA** や **ISO** などのセイバーメトリクス指標を一括計算し、並び替え可能な一覧表として表示します。")

# サンプルデータ作成用関数
@st.cache_data
def get_sample_csv():
    # 阪神タイガースの参考データ（2023年風）
    sample_data = {
        "選手名": ["近本 光司", "大山 悠輔", "佐藤 輝明", "中野 拓夢", "森下 翔太", "木浪 聖也", "梅野 隆太郎", "坂本 誠志郎", "ノイジー"],
        "打数": [501, 513, 448, 552, 350, 408, 237, 244, 475],
        "安打": [143, 147, 108, 157, 83, 109, 46, 55, 114],
        "二塁打": [24, 29, 21, 16, 14, 22, 5, 5, 13],
        "三塁打": [12, 0, 4, 5, 1, 1, 0, 1, 0],
        "本塁打": [8, 19, 24, 2, 10, 1, 1, 0, 9],
        "四球": [46, 54, 54, 28, 29, 30, 26, 17, 34],
        "死球": [4, 4, 0, 1, 6, 3, 2, 4, 0],
        "犠飛": [1, 2, 2, 3, 3, 3, 2, 2, 3]
    }
    df = pd.DataFrame(sample_data)
    # 日本語エクセルで開いたときに文字化けしないよう shift-jis で出力（またはutf-8-sig）
    return df.to_csv(index=False).encode('shift-jis')

# サイドバーによる操作パネル
st.sidebar.header("📂 データの読み込み")
uploaded_file = st.sidebar.file_uploader("選手成績のCSVファイルをアップロードしてください", type=["csv"])

st.sidebar.markdown("---")
st.sidebar.markdown("**💡 サンプルCSVデータのダウンロード**")
st.sidebar.markdown("お手元にデータがない場合は、こちらから阪神風の参考データCSVをダウンロードし、上の枠にアップロードしてお試しください。")
st.sidebar.download_button(
    label="⬇️ サンプルCSV",
    data=get_sample_csv(),
    file_name="sample_tigers_stats.csv",
    mime="text/csv",
)

if uploaded_file is not None:
    # エンコーディングの判定と読み込み
    try:
        # ExcelからそのままCSV保存した場合は shift-jis のことが多い
        df = pd.read_csv(uploaded_file, encoding="shift-jis")
    except UnicodeDecodeError:
        try:
            # UTF-8 で再試行
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding="utf-8-sig")
        except Exception as e:
            st.error(f"ファイルの読み込みに失敗しました。詳細: {e}")
            st.stop()
    
    # 必須カラムが含まれているかチェック
    required_cols = ["選手名", "打数", "安打", "二塁打", "三塁打", "本塁打", "四球", "死球", "犠飛"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        st.error(f"⚠️ アップロードされたCSVに以下の必要な項目が見つかりません。列名を以下のように合わせてください。\n\n不足列: `{', '.join(missing_cols)}`")
        st.warning("※ 必須項目: 選手名, 打数, 安打, 二塁打, 三塁打, 本塁打, 四球, 死球, 犠飛")
    else:
        st.success("✅ CSVの読み込みに成功しました！各指標を自動計算しました。**表の「wOBA」などをクリックすると並び替え（ソート）が可能です。**")
        
        # 指標の計算
        df["単打"] = df["安打"] - (df["二塁打"] + df["三塁打"] + df["本塁打"])
        
        # AVG
        df["AVG"] = df.apply(lambda row: row["安打"] / row["打数"] if row["打数"] > 0 else 0, axis=1)
        
        # OBP
        df["OBP"] = df.apply(lambda row: (row["安打"] + row["四球"] + row["死球"]) / 
                                        (row["打数"] + row["四球"] + row["死球"] + row["犠飛"]) 
                                        if (row["打数"] + row["四球"] + row["死球"] + row["犠飛"]) > 0 else 0, axis=1)
                                        
        # SLG
        df["塁打数"] = df["単打"] + 2 * df["二塁打"] + 3 * df["三塁打"] + 4 * df["本塁打"]
        df["SLG"] = df.apply(lambda row: row["塁打数"] / row["打数"] if row["打数"] > 0 else 0, axis=1)
        
        # OPS
        df["OPS"] = df["OBP"] + df["SLG"]
        
        # ISO (長打力)
        df["ISO"] = df["SLG"] - df["AVG"]
        
        # wOBA
        def calc_woba(row):
            numerator = 0.69 * row["四球"] + 0.72 * row["死球"] + 0.89 * row["単打"] + \
                        1.27 * row["二塁打"] + 1.62 * row["三塁打"] + 2.10 * row["本塁打"]
            denominator = row["打数"] + row["四球"] + row["犠飛"] + row["死球"]
            return numerator / denominator if denominator > 0 else 0
            
        df["wOBA"] = df.apply(calc_woba, axis=1)
        
        # 表示用のフォーマット整形（表示に最適化）
        df_display = df[["選手名", "打数", "安打", "本塁打", "AVG", "OPS", "ISO", "wOBA"]].copy()
        
        # 内部的には数値のままにしてソートを正しく機能させるため、Streamlitのcolumn_configでのフォーマットを指定します
        
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "AVG": st.column_config.NumberColumn("打率 (AVG)", format="%.3f"),
                "OPS": st.column_config.NumberColumn("OPS", format="%.3f"),
                "ISO": st.column_config.NumberColumn("ISO (長打力)", format="%.3f"),
                "wOBA": st.column_config.NumberColumn("wOBA", format="%.3f"),
                "打数": st.column_config.NumberColumn("打数"),
                "安打": st.column_config.NumberColumn("安打"),
                "本塁打": st.column_config.NumberColumn("本塁打"),
            }
        )
        
        st.markdown("### 📊 セイバーメトリクス指標の目安")
        st.markdown("""
        * **OPS (On-Base Plus Slugging)**: 打席あたりの総合的な得点貢献度の高さ。.800以上で優秀、.900以上で極めて優秀な打者。
        * **ISO (Isolated Power)**: 長打力を示す指標（長打率ー打率）。.200以上で優秀とされる。
        * **wOBA (Weighted On-Base Average)**: 四死球や長打など、各プレーの得点価値を加味した出塁の質を示す総合打撃指標。.340前後が平均、.400を超えれば超一流。
        """)

else:
    st.info("👈 左側のメニューからCSVファイルをアップロードしてください。またはサンプルデータをご活用ください。")
