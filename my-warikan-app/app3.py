import streamlit as st
import pandas as pd
import math

# --- ページの初期設定 ---
st.set_page_config(page_title="スマート割り勘アプリ", page_icon="💸", layout="centered")

# --- session_stateの初期化 ---
# アプリの再実行間でデータを保持するために使用
if 'members' not in st.session_state:
    st.session_state.members = []  # 参加メンバーのリスト
if 'payments' not in st.session_state:
    st.session_state.payments = [] # 支払い記録のリスト
if 'deleted_payments' not in st.session_state:
    st.session_state.deleted_payments = [] # 削除された支払い記録

# --- コールバック関数（Enterでメンバーを追加） ---
def add_member_on_enter():
    new_member = st.session_state.get("new_member_input", "").strip()
    if new_member and new_member not in st.session_state.members:
        st.session_state.members.append(new_member)
    # 入力フィールドをクリアするためのキー操作は不要（Streamlitが管理）

st.title("スマート割り勘アプリ 💸")

# --- メンバー登録 ---
st.header("メンバー登録")
st.text_input(
    "新しいメンバーの名前",
    key="new_member_input",
    on_change=add_member_on_enter,
    placeholder="名前を入力してEnterキーを押してください"
)

# --- 登録済みメンバーの表示と削除 ---
if st.session_state.members:
    with st.expander("登録済みメンバーの確認・削除"):
        members_to_delete = st.multiselect(
            "削除したいメンバーを選択してください",
            options=st.session_state.members
        )
        if st.button("選択したメンバーを削除", type="secondary"):
            # メンバーリストと、そのメンバーが行った支払いを削除
            st.session_state.members = [m for m in st.session_state.members if m not in members_to_delete]
            st.session_state.payments = [p for p in st.session_state.payments if p['支払った人'] not in members_to_delete]
            st.success(f"選択されたメンバーを削除しました。")
            st.experimental_rerun() # 画面を再読み込みして表示を更新

    st.caption("**現在のメンバー:** " + "、 ".join(st.session_state.members))


st.divider() # 区切り線

# --- 支払い登録 ---
st.header("支払い登録")
if st.session_state.members:
    with st.form("payment_form", clear_on_submit=True):
        payer = st.selectbox("支払った人", options=st.session_state.members)
        amount = st.number_input("金額 (円)", value=None, placeholder="例: 5000")
        memo = st.text_input("内容（メモ）", placeholder="例: 夕食代")
        
        if st.form_submit_button("この支払いを登録"):
            if amount and amount > 0:
                payment_record = {"支払った人": payer, "金額": amount, "内容": memo}
                st.session_state.payments.append(payment_record)
            else:
                st.warning("有効な金額を入力してください。")

else:
    st.info("まず、メンバーを1人以上登録してください。")

st.divider()

# --- 支払い履歴の表示と削除 ---
st.header("支払い履歴")
if not st.session_state.payments:
    st.info("支払いはまだ登録されていません。")
else:
    # 削除ボタンを各行に設置するため、ループ処理
    for i, payment in enumerate(st.session_state.payments):
        col1, col2, col3, col4 = st.columns([2, 2, 3, 1.5])
        with col1:
            st.write(f"**{payment['支払った人']}**")
        with col2:
            st.write(f"{payment['金額']:,} 円")
        with col3:
            st.write(payment['内容'])
        with col4:
            # 各ボタンにユニークなキーを設定
            if st.button("削除", key=f"delete_{i}", type="secondary"):
                # 削除リストに移動させてから、現在のリストから削除
                deleted_item = st.session_state.payments.pop(i)
                st.session_state.deleted_payments.append(deleted_item)
                st.experimental_rerun() # 画面を再読み込み

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
        # ここから精算ロジック...
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

# --- 削除済み記録の表示 ---
if st.session_state.deleted_payments:
    with st.expander("削除済みの支払い記録を見る"):
        df_deleted = pd.DataFrame(st.session_state.deleted_payments)
        st.dataframe(df_deleted, hide_index=True)
