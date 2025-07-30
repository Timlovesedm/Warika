import streamlit as st
import pandas as pd
import math

# --- ページの初期設定 ---
st.set_page_config(page_title="スマート割り勘アプリ", page_icon="💸", layout="wide")

# --- session_stateの初期化 ---
if 'members' not in st.session_state:
    st.session_state.members = []  # 参加メンバーのリスト
if 'payments' not in st.session_state:
    st.session_state.payments = [] # 支払い記録のリスト

# --- コールバック関数（Enterでメンバーを追加） ---
def add_member_on_enter():
    new_member = st.session_state.new_member_input
    if new_member and new_member not in st.session_state.members:
        st.session_state.members.append(new_member)
    # 入力フィールドをクリアするためにキーをリセットするわけではない
    # Streamlitが自動で再実行時に値を保持するが、formの外なので手動クリアは難しい
    # placeholderで操作をガイドする

st.title("スマート割り勘アプリ 💸")

# --- 画面を2つのカラムに分割（左側を広く） ---
col1, col2 = st.columns([1.5, 1])


# --- 左カラム：入力エリア ---
with col1:
    st.header("メンバー登録")
    st.text_input(
        "新しいメンバーの名前",
        key="new_member_input",
        on_change=add_member_on_enter,
        placeholder="名前を入力してEnterキーを押してください"
    )

    # 登録済みメンバーを分かりやすく表示
    if st.session_state.members:
        st.caption("登録済み: " + "、 ".join(st.session_state.members))

    st.header("支払い登録")
    if st.session_state.members:
        with st.form("payment_form", clear_on_submit=True):
            payer = st.selectbox("支払った人", options=st.session_state.members, key="payer")
            amount = st.number_input("金額 (円)", min_value=1, step=1000, key="amount")
            memo = st.text_input("内容（メモ）", placeholder="例: 夕食代", key="memo")
            
            submitted = st.form_submit_button("この支払いを登録")
            if submitted:
                payment_record = {"支払った人": payer, "金額": amount, "内容": memo}
                st.session_state.payments.append(payment_record)
    else:
        st.info("まず、メンバーを1人以上登録してください。")

# --- 右カラム：状況と精算結果 ---
with col2:
    st.header("現在の状況")
    if not st.session_state.payments:
        st.info("支払いはまだ登録されていません。")
    else:
        # DataFrameを使って支払い履歴を綺麗に表示
        df_payments = pd.DataFrame(st.session_state.payments)
        st.dataframe(df_payments, hide_index=True)
    
    # --- 精算の実行 ---
    if st.button("精算する！", type="primary", use_container_width=True) and len(st.session_state.members) > 1:
        st.header("精算結果")

        paid_summary = {member: 0 for member in st.session_state.members}
        total_spent = sum(p['金額'] for p in st.session_state.payments)
        
        for payment in st.session_state.payments:
            paid_summary[payment['支払った人']] += payment['金額']
        
        cost_per_person = total_spent / len(st.session_state.members)

        # 結果をメトリックで表示
        st.metric(label="合計支出", value=f"{total_spent:,.0f} 円")
        st.metric(label="1人あたりの負担額", value=f"{cost_per_person:,.0f} 円", delta_color="off")

        # --- 精算方法の計算と表示 ---
        st.subheader("精算方法")
        balances = {member: paid_summary[member] - cost_per_person for member in st.session_state.members}
        
        debtors = {p: -b for p, b in balances.items() if b < 0}
        creditors = {p: b for p, b in balances.items() if b > 0}
        
        transactions = []
        while debtors and creditors:
            debtor_name, debtor_amount = max(debtors.items(), key=lambda item: item[1])
            creditor_name, creditor_amount = max(creditors.items(), key=lambda item: item[1])
            
            transfer_amount = min(debtor_amount, creditor_amount)
            
            # 視覚的に分かりやすいフォーマットで追加
            transactions.append(
                f"👤 **{debtor_name}** → 👤 **{creditor_name}** へ **{transfer_amount:,.0f} 円**"
            )
            
            debtors[debtor_name] -= transfer_amount
            creditors[creditor_name] -= transfer_amount
            
            if debtors[debtor_name] < 1: del debtors[debtor_name]
            if creditors[creditor_name] < 1: del creditors[creditor_name]

        if not transactions:
            st.success("🎉 精算は不要です！")
        else:
            for t in transactions:
                st.markdown(f"- {t}")

    elif len(st.session_state.members) <= 1 and st.session_state.payments:
         st.warning("精算するにはメンバーが2人以上必要です。")
