import streamlit as st
import pandas as pd
import math

# --- ページの初期設定 ---
st.set_page_config(page_title="最終版 割り勘アプリ", page_icon="🎯", layout="centered")

# --- Session Stateの初期化 ---
if 'members' not in st.session_state:
    st.session_state.members = []
if 'payments' not in st.session_state:
    st.session_state.payments = []
if 'editing_payment_index' not in st.session_state:
    st.session_state.editing_payment_index = None # 編集中の支払いID

# --- コールバック関数（Enterキーでメンバーを追加） ---
def add_member():
    new_member = st.session_state.get("new_member_input", "").strip()
    if new_member and new_member not in st.session_state.members:
        st.session_state.members.append(new_member)
    st.session_state.new_member_input = "" # 入力欄をクリア

st.title("最終版 割り勘アプリ 🎯")

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
            if st.button("×", key=f"delete_member_{member}", use_container_width=True):
                # メンバー削除時に、関連する支払いも削除
                st.session_state.payments = [p for p in st.session_state.payments if p['支払った人'] != member]
                st.session_state.members.remove(member)
                # エラー防止：編集状態をリセット
                st.session_state.editing_payment_index = None
                st.rerun()

st.divider()

# --- 支払い登録・編集 ---
# 編集モードかどうかに応じてヘッダーとボタンのテキストを変更
is_editing = st.session_state.editing_payment_index is not None
header_text = "支払いを編集" if is_editing else "支払い登録"
button_text = "更新する" if is_editing else "登録する"

st.header(header_text)
if st.session_state.members:
    editing_defaults = {}
    if is_editing:
        # 編集中の支払いが存在することを確認
        if st.session_state.editing_payment_index < len(st.session_state.payments):
            editing_payment = st.session_state.payments[st.session_state.editing_payment_index]
            editing_defaults = {
                "payer": editing_payment["支払った人"],
                "amount": editing_payment["金額"],
                "memo": editing_payment["内容"]
            }

    with st.form("payment_form"):
        # 編集中のデータが存在し、その人がメンバーリストにいる場合、その人をデフォルトで選択
        default_payer_index = 0
        if "payer" in editing_defaults and editing_defaults["payer"] in st.session_state.members:
            default_payer_index = st.session_state.members.index(editing_defaults["payer"])
        
        payer = st.selectbox("支払った人", options=st.session_state.members, index=default_payer_index)
        amount = st.number_input("金額 (円)", value=editing_defaults.get("amount"), placeholder="例: 5000", step=1, format="%d")
        memo = st.text_input("内容（メモ）", value=editing_defaults.get("memo", ""), placeholder="例: 夕食代")
        
        if st.form_submit_button(button_text):
            if amount and amount > 0:
                new_payment = {"支払った人": payer, "金額": int(amount), "内容": memo}
                if is_editing:
                    st.session_state.payments[st.session_state.editing_payment_index] = new_payment
                    st.success("支払いを更新しました。")
                else:
                    st.session_state.payments.append(new_payment)
                    st.success("支払いを登録しました。")
                # フォームをリセットするために編集状態を解除
                st.session_state.editing_payment_index = None
                st.rerun()
            else:
                st.warning("有効な金額を入力してください。")
else:
    st.info("まず、メンバーを1人以上登録してください。")

st.divider()

# --- 支払い履歴の表示 ---
st.header("支払い履歴")
if st.session_state.payments:
    for i, payment in enumerate(st.session_state.payments):
        col1, col2, col3, col4, col5 = st.columns([2.5, 2, 3, 1, 1])
        with col1:
            st.write(f"**{payment['支払った人']}**")
        with col2:
            st.write(f"{payment['金額']:,} 円")
        with col3:
            st.write(payment['内容'])
        with col4:
            if st.button("編集", key=f"edit_{i}"):
                st.session_state.editing_payment_index = i
                st.rerun()
        with col5:
            if st.button("×", key=f"delete_payment_{i}"):
                st.session_state.payments.pop(i)
                # エラー防止：編集状態をリセット
                st.session_state.editing_payment_index = None
                st.rerun()
else:
    st.info("支払いはまだ登録されていません。")

st.divider()

# --- 精算 ---
st.header("精算")
if st.button("精算する！", type="primary", use_container_width=True):
    # 精算ロジックは変更なし
    if len(st.session_state.members) > 1 and st.session_state.payments:
        total_spent = sum(p['金額'] for p in st.session_state.payments)
        cost_per_person = total_spent / len(st.session_state.members)
        
        paid_summary = {member: 0 for member in st.session_state.members}
        for p in st.session_state.payments:
            paid_summary[p['支払った人']] += p['金額']
        
        balances = {m: paid_summary[m] - cost_per_person for m in st.session_state.members}
        
        st.metric(label="合計支出", value=f"{total_spent:,.0f} 円")
        st.metric(label="1人あたりの負担額", value=f"{math.ceil(cost_per_person):,.0f} 円")

        st.subheader("精算方法")
        debtors = {p: -b for p, b in balances.items() if b < 0}
        creditors = {p: b for p, b in balances.items() if b > 0}
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
