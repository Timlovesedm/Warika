import streamlit as st
import math

# --- 画面の構成 ---
st.set_page_config(page_title="割り勘アプリ", page_icon="💸")

st.title("割り勘アプリ 💸")

# 金額と人数の入力欄を設置
total_amount = st.number_input("合計金額を入力してください", min_value=0, step=100)
num_people = st.number_input("人数を入力してください", min_value=1, step=1)

# 計算ボタン
if st.button("計算する"):
    # 入力値のチェック
    if total_amount > 0 and num_people > 0:
        # 割り勘を計算
        amount_per_person = total_amount / num_people
        
        # 100円単位で切り上げ
        rounded_amount = math.ceil(amount_per_person / 100) * 100
        remainder = (rounded_amount * num_people) - total_amount

        # 結果を表示
        st.success(f"1人あたり: {rounded_amount:,} 円です")
        st.info(f"（合計: {rounded_amount * num_people:,} 円、端数: {remainder:,} 円）")
    else:
        # エラーメッセージ
        st.error("正しい金額と人数を入力してください。")