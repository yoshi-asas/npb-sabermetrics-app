import streamlit as st
import pandas as pd

st.title("🏆 セ・リーグ 順位表 (サンプル)")
st.markdown("こちらは別ページで表示している順位表のサンプルです。データは自由にカスタマイズ可能です。")

# サンプルの順位表データ
data = {
    "順位": [1, 2, 3, 4, 5, 6],
    "チーム": ["阪神タイガース", "広島東洋カープ", "横浜DeNAベイスターズ", "読売ジャイアンツ", "東京ヤクルトスワローズ", "中日ドラゴンズ"],
    "試合": [143, 143, 143, 143, 143, 143],
    "勝利": [85, 74, 74, 71, 57, 56],
    "敗北": [53, 65, 66, 70, 83, 82],
    "引分": [5, 4, 3, 2, 3, 5],
    "勝率": [0.616, 0.532, 0.529, 0.504, 0.407, 0.406],
    "ゲーム差": ["-", "11.5", "12.0", "15.5", "29.0", "29.0"]
}

df_standings = pd.DataFrame(data)

st.dataframe(
    df_standings,
    use_container_width=True,
    hide_index=True,
    column_config={
        "勝率": st.column_config.NumberColumn("勝率", format="%.3f")
    }
)
