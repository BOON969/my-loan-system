# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime

st.set_page_config(page_title="My Loan System", layout="wide")

# --- Language Config / 语言配置 ---
LANGUAGES = {
    "English": {
        "title": "SYSTEM LOGIN",
        "user_id": "User ID",
        "password": "Password",
        "login_btn": "Login",
        "input_warn": "Please enter ID and Password",
        "unauth": "Unauthorized Access: This ID is not allowed.",
        "login_fail": "Login Failed: Incorrect Password or System Error",
        "logout": "Logout",
        "menu": "Menu",
        "dashboard": "Dashboard",
        "new_loan": "New Loan",
        "repayment": "Repayment",
        "expenses": "Expenses",
        "overview": "Overview",
        "no_records": "No records found",
        "error_load": "Error loading data.",
        "add_customer": "Add Customer",
        "name": "Name",
        "ic": "IC No",
        "amount": "Total Amount",
        "fee": "Fee",
        "interest": "Interest",
        "actual_get": "Actual Get",
        "repay_method": "Repayment",
        "weekly": "Weekly",
        "monthly": "Monthly",
        "who": "Who Issued",
        "account": "Account",
        "submit": "Submit",
        "saved": "Saved: {}",
        "save_fail": "Save failed: {}",
        "user_label": "User: {}",
        "select_cust": "Select Customer",
        "total_paid": "Total Paid",
        "deduct_int": "Deduct Interest",
        "deduct_prin": "Deduct Principal",
        "handler": "Handler",
        "new_bal": "New Balance",
        "repay_success": "Repayment Recorded! New Balance: {}",
        "exp_cat": "Category",
        "exp_amt": "Amount",
        "exp_remark": "Remark",
        "exp_saved": "Expense Saved"
    },
    "中文": {
        "title": "系统登录",
        "user_id": "用户 ID",
        "password": "密码",
        "login_btn": "登录",
        "input_warn": "请输入 ID 和密码",
        "unauth": "无权访问：该 ID 不在允许列表中。",
        "login_fail": "登录失败：密码错误或系统错误",
        "logout": "退出登录",
        "menu": "菜单",
        "dashboard": "数据大盘",
        "new_loan": "新增客户",
        "repayment": "客户还款",
        "expenses": "杂费支出",
        "overview": "业务概览",
        "no_records": "暂无数据",
        "error_load": "加载数据失败",
        "add_customer": "录入新单",
        "name": "姓名",
        "ic": "IC/证件号",
        "amount": "总数 (Total)",
        "fee": "手续费",
        "interest": "利息",
        "actual_get": "实得 (Actual)",
        "repay_method": "还款方式",
        "weekly": "按周",
        "monthly": "按月",
        "who": "谁出 (Who)",
        "account": "账号 (Ac)",
        "submit": "提交保存",
        "saved": "已保存: {}",
        "save_fail": "保存失败: {}",
        "user_label": "用户: {}",
        "select_cust": "选择客户",
        "total_paid": "实收总额",
        "deduct_int": "扣利息",
        "deduct_prin": "退母 (还本金)",
        "handler": "经手人",
        "new_bal": "剩余余额",
        "repay_success": "还款成功！剩余余额: {}",
        "exp_cat": "类别",
        "exp_amt": "金额",
        "exp_remark": "备注",
        "exp_saved": "支出已保存"
    }
}

# Whitelist
ALLOWED_USERS = ["BOON", "WILLIAM"]

# Connect DB
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_ANON_KEY"])
except:
    st.error("Key Error: Please check secrets.toml")
    st.stop()

# Session
if "user" not in st.session_state:
    st.session_state.user = None
if "lang" not in st.session_state:
    st.session_state.lang = "English"

# --- Sidebar ---
with st.sidebar:
    st.session_state.lang = st.radio("Language / 语言", ["English", "中文"])

T = LANGUAGES[st.session_state.lang]

# --- Login ---
if not st.session_state.user:
    st.markdown("### {}".format(T['title']))
    col1, col2 = st.columns([1, 2])
    with col1:
        user_id = st.text_input(T['user_id'])
        password = st.text_input(T['password'], type="password")
        
        if st.button(T['login_btn']):
            if not user_id or not password:
                st.warning(T['input_warn'])
            else:
                clean_id = user_id.strip().upper()
                if clean_id not in ALLOWED_USERS:
                     st.error(T['unauth'])
                else:
                    email = "{}@myloans.com".format(clean_id)
                    try:
                        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                        st.session_state.user = res.user
                        st.rerun()
                    except Exception as e:
                        st.error(T['login_fail'])
    st.stop()

# --- Main App ---
with st.sidebar:
    u_email = st.session_state.user.email
    user_name = u_email.split('@')[0].upper()
    st.success(T['user_label'].format(user_name))
    
    if st.button(T['logout']):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun()
    
    st.divider()
    menu = st.radio(T['menu'], [T['dashboard'], T['new_loan'], T['repayment'], T['expenses']])

# 1. Dashboard
if menu == T['dashboard']:
    st.subheader(T['overview'])
    try:
        # Load Loans
        res = supabase.table("loans").select("*").execute()
        if res.data:
            df = pd.DataFrame(res.data)
            st.markdown("#### Loans / 贷款")
            st.dataframe(df, use_container_width=True)
        else:
            st.info(T['no_records'] + " (Loans)")
            
        st.divider()
        
        # Load Expenses
        try:
            res_exp = supabase.table("expenses").select("*").execute()
            if res_exp.data:
                df_exp = pd.DataFrame(res_exp.data)
                st.markdown("#### Expenses / 支出")
                st.dataframe(df_exp, use_container_width=True)
        except:
            pass # Table might not exist yet

    except Exception as e:
        st.error(T['error_load'])
        st.error(str(e))

# 2. New Loan
elif menu == T['new_loan']:
    st.subheader(T['add_customer'])
    with st.form("add"):
        c1, c2 = st.columns(2)
        name = c1.text_input(T['name'])
        ic = c2.text_input(T['ic'])
        
        c3, c4 = st.columns(2)
        amt = c3.number_input(T['amount'], min_value=0.0)
        fee = c4.number_input(T['fee'], min_value=0.0)
        
        c5, c6 = st.columns(2)
        interest = c5.number_input(T['interest'], min_value=0.0)
        actual_get = amt - fee # Auto calc logic from user code
        c6.metric(T['actual_get'], actual_get)
        
        method = st.selectbox(T['repay_method'], [T['weekly'], T['monthly']])
        
        c7, c8 = st.columns(2)
        who = c7.text_input(T['who'])
        account = c8.text_input(T['account'])
        
        if st.form_submit_button(T['submit']):
            try:
                data = {
                    "name": name, 
                    "ic": ic, 
                    "loan_amount": amt, 
                    "fee": fee,
                    "interest": interest,
                    "actual_get": actual_get, 
                    "balance": amt, # Initial balance = Loan Amount
                    "repay_method": method,
                    "who_issued": who,
                    "account_no": account,
                    "created_at": datetime.now().isoformat()
                }
                supabase.table("loans").insert(data).execute()
                st.success(T['saved'].format(name))
            except Exception as e:
                st.error(T['save_fail'].format(e))

# 3. Repayment
elif menu == T['repayment']:
    st.subheader(T['repayment'])
    
    # Fetch Active Loans
    loans = []
    try:
        res = supabase.table("loans").select("id, name, balance").gt("balance", 0).execute()
        loans = res.data
    except:
        st.error("Error fetching loans")
    
    if not loans:
        st.info("No active loans found.")
    else:
        # Create a dictionary for dropdown: "Name (Bal: 1000)" -> ID
        loan_options = {"{} (Bal: {})".format(l['name'], l['balance']): l for l in loans}
        selected_label = st.selectbox(T['select_cust'], list(loan_options.keys()))
        selected_loan = loan_options[selected_label]
        
        with st.form("repay"):
            c1, c2 = st.columns(2)
            total_paid = c1.number_input(T['total_paid'], min_value=0.0)
            handler = c2.text_input(T['handler'], value=user_name)
            
            c3, c4 = st.columns(2)
            deduct_int = c3.number_input(T['deduct_int'], min_value=0.0)
            deduct_prin = c4.number_input(T['deduct_prin'], min_value=0.0)
            
            if st.form_submit_button(T['submit']):
                new_balance = selected_loan['balance'] - deduct_prin
                
                # 1. Update Loan Balance
                supabase.table("loans").update({"balance": new_balance}).eq("id", selected_loan['id']).execute()
                
                # 2. Insert Repayment Record
                repay_data = {
                    "loan_id": selected_loan['id'],
                    "customer_name": selected_loan['name'],
                    "amount_paid": total_paid,
                    "interest_part": deduct_int,
                    "principal_part": deduct_prin,
                    "balance_after": new_balance,
                    "handler": handler,
                    "created_at": datetime.now().isoformat()
                }
                supabase.table("repayments").insert(repay_data).execute()
                
                st.success(T['repay_success'].format(new_balance))
                # st.rerun() # Refresh to update dropdown balance

# 4. Expenses
elif menu == T['expenses']:
    st.subheader(T['expenses'])
    with st.form("exp"):
        category = st.text_input(T['exp_cat']) # e.g. Food, Transport
        customer = st.text_input(T['select_cust'] + " (Optional)")
        amount = st.number_input(T['exp_amt'], min_value=0.0)
        handler = st.text_input(T['handler'], value=user_name)
        remark = st.text_area(T['exp_remark'])
        
        if st.form_submit_button(T['submit']):
            exp_data = {
                "category": category,
                "customer_name": customer,
                "amount": amount,
                "handler": handler,
                "remark": remark,
                "created_at": datetime.now().isoformat()
            }
            try:
                supabase.table("expenses").insert(exp_data).execute()
                st.success(T['exp_saved'])
            except Exception as e:
                st.error(T['save_fail'].format(e))
