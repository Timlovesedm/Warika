import streamlit as st
import pandas as pd
import math

# --- ページの初期設定 ---
st.set_page_config(page_title="割り勘＆精算アプリ", page_icon="💰", layout="centered")

# --- Session Stateの初期化 ---
if 'members' not in st.session_state:
    st.session_state.members = []
if 'payments' not in st.session_state:
    st.session_state.payments = []

# --- コールバック関数（Enterキーでメンバーを追加） ---
def add_member():
    new_member = st.session_state.get("new_member_input", "").strip()
    if new_member and new_member not in st.session_state.members:
        st.session_state.members.append(new_member)
    st.session_state.new_member_input = "" # 入力欄をクリア

st.title("割り勘＆精算アプリ 💰")

# --- メンバー登録 ---
st.header("メンバー登録")
st.text_input(
    "新しいメンバーの名前",
    key="new_member_input",
    on_change=add_member,
    placeholder="名前を入力してEnterキーを押してください"
)

# --- 登録済みメンバーの表示と削除 ---
if st.session_state.members:
    st.subheader("現在のメンバー")
    for member in st.session_state.members:
        col1, col2 = st.columns([0.85, 0.15])
        with col1:
            st.markdown(f"""<div style="padding: 8px 12px; background-color: #f0f2f6; border-radius: 8px;">{member}</div>""", unsafe_allow_html=True)
        with col2:
            if st.button("×", key=f"delete_{member}", use_container_width=True):
                st.session_state.members.remove(member)
                # メンバー削除時にその人の支払いも削除
                st.session_state.payments = [p for p in st.session_state.payments if p['支払った人'] != member]
                st.experimental_rerun()

st.divider()

# --- 支払い登録 ---
st.header("支払い登録")
if st.session_state.members:
    with st.form("payment_form", clear_on_submit=True):
        payer = st.selectbox("支払った人", options=st.session_state.members)
        amount = st.number_input("金額 (円)", value=None, placeholder="例: 5000")
        memo = st.text_input("内容（メモ）", placeholder="例: 夕食代")
        
        if st.form_submit_button("この支払いを登録"):
            if amount and amount > 0:
                st.session_state.payments.append({"支払った人": payer, "金額": amount, "内容": memo})
            else:
                st.warning("有効な金額を入力してください。")
else:
    st.info("まず、メンバーを1人以上登録してください。")

# --- 支払い履歴の表示 ---
if st.session_state.payments:
    st.subheader("支払い履歴")
    df_payments = pd.DataFrame(st.session_state.payments)
    st.dataframe(df_payments, hide_index=True, use_container_width=True)

st.divider()

# --- 精算 ---
st.header("精算")
if st.button("精算する！", type="primary", use_container_width=True):
    if len(st.session_state.members) > 1 and st.session_state.payments:
        total_spent = sum(p['金額'] for p in st.session_state.payments)
        cost_per_person = total_spent / len(st.session_state.members)
        
        paid_summary = {member: 0 for member in st.session_state.members}
        for p in st.session_state.payments:
            paid_summary[p['支払った人']] += p['金額']
        
        balances = {m: paid_summary[m] - cost_per_person for m in st.session_state.members}
        debtors = {p: -b for p, b in balances.items() if b < 0}
        creditors = {p: b for p, b in balances.items() if b > 0}
        
        # 結果表示
        st.metric(label="合計支出", value=f"{total_spent:,.0f} 円")
        st.metric(label="1人あたりの負担額", value=f"{math.ceil(cost_per_person):,.0f} 円")

        st.subheader("精算方法")
        transactions = []
        while debtors and creditors:
            debtor_name, debtor_amount = max(debtors.items(), key=lambda item: item[1])
            creditor_name, creditor_amount = max(creditors.items(), key=lambda item: item[1])
            transfer_amount = min(debtor_amount, creditor_amount)
            transactions.append(f"👤 **{debtor_name}** → 👤 **{creditor_name}** へ **{math.ceil(transfer_amount):,.0f} 円**")
            debtors[debtor_name] -= transfer_amount
            creditors[creditor_name] -= transfer_amount
            if debtors[debtor_name] < 1: del debtors[debtor_name]
            if creditors[creditor_name] < 1: del creditors[creditor_name]

        if not transactions:
            st.success("🎉 精算は不要です！")
        else:
            for t in transactions:
                st.markdown(f"- {t}")

    else:
        st.warning("精算するには、2人以上のメンバーと1件以上の支払いが必要です。")
