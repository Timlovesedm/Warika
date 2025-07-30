import streamlit as st
import pandas as pd

# --- ページの初期設定 ---
st.set_page_config(page_title="高機能割り勘アプリ", page_icon="📊", layout="wide")

# --- session_stateの初期化 ---
# アプリの再実行間でデータを保持するために使用
if 'members' not in st.session_state:
    st.session_state.members = []  # 参加メンバーのリスト
if 'payments' not in st.session_state:
    st.session_state.payments = [] # 支払い記録のリスト

st.title("高機能 割り勘アプリ 📊")
st.write("メンバーを登録し、それぞれの支払い記録を追加してください。最後に自動で精算します。")

# --- 画面を2つのカラムに分割 ---
col1, col2 = st.columns(2)


# --- 左カラム：入力と登録 ---
with col1:
    st.header("1. メンバー登録")
    new_member = st.text_input("新しいメンバーの名前", key="new_member_input")
    if st.button("メンバーを追加"):
        if new_member and new_member not in st.session_state.members:
            st.session_state.members.append(new_member)
            st.success(f"「{new_member}」さんを登録しました。")
        elif not new_member:
            st.warning("名前を入力してください。")
        else:
            st.warning(f"「{new_member}」さんは既に登録済みです。")

    st.header("2. 支払い登録")
    # メンバーが登録されている場合のみ支払い登録フォームを表示
    if st.session_state.members:
        with st.form("payment_form", clear_on_submit=True):
            payer = st.selectbox("支払った人", options=st.session_state.members)
            amount = st.number_input("金額", min_value=1, step=100)
            memo = st.text_input("内容（メモ）")
            
            submitted = st.form_submit_button("この支払いを登録")
            if submitted:
                payment_record = {"payer": payer, "amount": amount, "memo": memo}
                st.session_state.payments.append(payment_record)
                st.success(f"「{payer}」さんの{amount:,}円（{memo}）の支払いを登録しました。")
    else:
        st.info("まずメンバーを1人以上登録してください。")


# --- 右カラム：現在の状況と精算結果 ---
with col2:
    st.header("現在の状況")

    # 登録メンバーの表示
    if st.session_state.members:
        st.subheader("登録メンバー")
        st.write("、".join(st.session_state.members))
    
    # 支払い履歴の表示
    if st.session_state.payments:
        st.subheader("支払い履歴")
        # pandasのDataFrameを使って見やすく表示
        df_payments = pd.DataFrame(st.session_state.payments)
        df_payments.rename(columns={'payer': '支払った人', 'amount': '金額', 'memo': '内容'}, inplace=True)
        st.dataframe(df_payments)
    
    # --- 精算の実行 ---
    if st.button("精算する！", type="primary") and len(st.session_state.members) > 0:
        st.header("3. 精算結果")

        # 各メンバーの支払い合計を計算
        paid_summary = {member: 0 for member in st.session_state.members}
        total_spent = 0
        for payment in st.session_state.payments:
            paid_summary[payment['payer']] += payment['amount']
            total_spent += payment['amount']
        
        # 1人あたりの負担額を計算
        cost_per_person = total_spent / len(st.session_state.members)

        # 各メンバーの貸し借り金額を計算
        balances = {member: paid_summary[member] - cost_per_person for member in st.session_state.members}
        
        # 結果表示
        st.subheader("各メンバーの支払い状況")
        st.write(f"**合計支出:** {total_spent:,.0f} 円")
        st.write(f"**1人あたりの負担額:** {cost_per_person:,.0f} 円")

        for member, paid in paid_summary.items():
            st.write(f"・**{member}さん:** {paid:,.0f} 円を支払済み")

        # 誰が誰に支払うかを計算
        debtors = {person: -balance for person, balance in balances.items() if balance < 0} # 支払う人
        creditors = {person: balance for person, balance in balances.items() if balance > 0} # 受け取る人
        
        transactions = []
        
        st.subheader("精算方法")
        if not debtors:
            st.success("全員の支払いが完了しており、精算は不要です！")
        else:
            # 簡潔な精算アルゴリズム
            while debtors and creditors:
                debtor_name, debtor_amount = max(debtors.items(), key=lambda item: item[1])
                creditor_name, creditor_amount = max(creditors.items(), key=lambda item: item[1])

                transfer_amount = min(debtor_amount, creditor_amount)
                
                transactions.append(f"**{debtor_name}** さん → **{creditor_name}** さん へ **{transfer_amount:,.0f} 円** 支払う")
                
                debtors[debtor_name] -= transfer_amount
                creditors[creditor_name] -= transfer_amount

                if debtors[debtor_name] < 1: del debtors[debtor_name]
                if creditors[creditor_name] < 1: del creditors[creditor_name]

            for t in transactions:
                st.markdown(f"- {t}")
