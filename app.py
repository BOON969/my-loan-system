# # -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime, timedelta

st.set_page_config(page_title="贷款管理系统 (Loan System)", layout="wide")

# --- Hide Streamlit Style & Mobile Optimization & Deep Dark Theme ---
hide_streamlit_style = """
            <style>
            /* Hide Streamlit Default Elements (Aggressive) */
            #MainMenu {visibility: hidden !important;}
            footer {visibility: hidden !important;}
            header {visibility: hidden !important;}
            .stDeployButton {display: none !important;}
            [data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
            [data-testid="stDecoration"] {visibility: hidden !important;}
            [data-testid="stStatusWidget"] {visibility: hidden !important;}
            [data-testid="stHeader"] {display: none !important;}
            div[data-testid="stToolbar"] {display: none !important;}
            .viewerBadge_container__1QSob {display: none !important;}
            
            /* Deep Dark Theme Overrides */
            .stApp {
                background-color: #0E1117;
                font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            }
            div[data-testid="stSidebar"] {
                background-color: #262730;
                border-right: 1px solid #333;
            }
            
            /* Enhanced Custom Cards for Metrics */
            div[data-testid="stMetric"] {
                background-color: #1E1E1E;
                border: 1px solid #333;
                padding: 15px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.3);
                transition: transform 0.2s;
            }
            div[data-testid="stMetric"]:hover {
                transform: translateY(-2px);
                border-color: #444;
            }
            
            /* Button Styling */
            .stButton button {
                background: linear-gradient(to right, #2E86C1, #1B4F72);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                transition: all 0.3s ease;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            }
            .stButton button:hover {
                background: linear-gradient(to right, #3498DB, #2874A6);
                box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                transform: translateY(-1px);
            }
            
            /* Input Fields */
            .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
                background-color: #0E1117;
                border: 1px solid #444;
                border-radius: 6px;
                color: #FFF;
            }
            
            /* Custom Cards */
            div.css-1r6slb0.e1tzin5v2 {
                background-color: #1E1E1E;
                border: 1px solid #333;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            
            /* Typography */
            h1, h2, h3 {
                color: #E0E0E0;
                font-weight: 600;
            }
            p, label {
                color: #B0B0B0;
            }
            
            /* Mobile Optimization (Phone Version) */
            @media (max-width: 768px) {
                /* Make buttons larger and full width for touch */
                .stButton button {
                    width: 100%;
                    padding-top: 12px;
                    padding-bottom: 12px;
                    font-size: 18px !important;
                    font-weight: bold;
                    border-radius: 12px;
                    margin-top: 10px;
                }
                
                /* Increase input height for easier tapping */
                .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
                    min-height: 50px;
                    font-size: 16px;
                    border-radius: 10px;
                }
                
                /* Card-like styling for metrics on mobile */
                [data-testid="stMetric"] {
                    background-color: #1E1E1E;
                    padding: 15px;
                    border-radius: 10px;
                    margin-bottom: 10px;
                    border: 1px solid #333;
                }
                
                /* Adjust table font size */
                .stDataFrame {
                    font-size: 14px;
                }
            }
            
            /* General UI Polish */
            .stMetricLabel {font-weight: bold; color: #888;}
            .stMetricValue {color: #00D4FF;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- Language Config / 语言配置 ---
LANGUAGES = {
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
        "phone": "电话号码",
        "ic": "IC/证件号",
        "amount": "总数 (Total)",
        "fee": "手续费",
        "interest": "利息",
        "actual_get": "实得 (Actual)",
        "loan_remark": "备注: 到手/需还",
        "repay_method": "还款方式",
        "repay_remark": "还款方式备注",
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
        "exp_saved": "支出已保存",
        "due_today": "今日到期 (Due Today)",
        "mark_paid": "已还款 ✅",
        "overdue": "逾期 (需罚款)",
        "days_overdue": "逾期天数",
        "add_penalty": "添加罚款",
        "penalty_amt": "罚款金额",
        "penalty_added": "罚款已添加!",
        "delete_loan": "删除用户",
        "delete_confirm": "确定删除吗？无法恢复。",
        "deleted": "用户已删除",
        "fin_summary": "本月财务概览",
        "total_income": "总收入金额",
        "total_loaned": "顾客贷款总金额",
        "total_int": "总收利息金额",
        "total_penalty": "总逾期罚款金额",
        "total_exp": "总支出金额",
        "net_profit": "总盈利金额"
    },
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
        "phone": "Phone No",
        "ic": "IC No",
        "amount": "Total Amount",
        "fee": "Fee",
        "interest": "Interest",
        "actual_get": "Actual Get",
        "loan_remark": "Note: Actual Get / Repayment",
        "repay_method": "Repayment Method",
        "repay_remark": "Repayment Note",
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
        "exp_saved": "Expense Saved",
        "due_today": "Due Today",
        "mark_paid": "Mark as Paid ✅",
        "overdue": "Overdue (Penalty Needed)",
        "days_overdue": "Days Overdue",
        "add_penalty": "Add Penalty",
        "penalty_amt": "Penalty Amount",
        "penalty_added": "Penalty Added!",
        "delete_loan": "Delete Loan",
        "delete_confirm": "Are you sure? This cannot be undone.",
        "deleted": "Loan Deleted",
        "fin_summary": "Financial Summary (This Month)",
        "total_income": "Total Income",
        "total_loaned": "Total Loaned",
        "total_int": "Total Interest",
        "total_penalty": "Total Penalty",
        "total_exp": "Total Expenses",
        "net_profit": "Net Profit"
    }
}

# Whitelist
ALLOWED_USERS = ["BOON", "WILLIAM"]

# --- Firewall Logic (Security) ---
@st.cache_resource
def get_login_tracker():
    # Stores failed attempts: { "user_id": [timestamp1, timestamp2, ...] }
    return {}

def check_firewall(user_id):
    tracker = get_login_tracker()
    now = datetime.now()
    
    if user_id in tracker:
        # Keep only attempts in the last 15 minutes
        tracker[user_id] = [t for t in tracker[user_id] if now - t < timedelta(minutes=15)]
        
        if len(tracker[user_id]) >= 3:
            return True, (timedelta(minutes=15) - (now - tracker[user_id][-1])).seconds // 60
            
    return False, 0

def log_failed_attempt(user_id):
    tracker = get_login_tracker()
    if user_id not in tracker:
        tracker[user_id] = []
    tracker[user_id].append(datetime.now())

# Connect DB
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_ANON_KEY"])
except Exception as e:
    st.error(f"Key Error: Please check secrets.toml. Detail: {e}")
    st.stop()

# Session
if "user" not in st.session_state:
    st.session_state.user = None
if "lang" not in st.session_state:
    st.session_state.lang = "中文" # Default to Chinese

def navigate_to(page):
    st.session_state.nav_menu = page

# --- Sidebar ---
with st.sidebar:
    # Changed default selection to Chinese first
    st.session_state.lang = st.radio("Language / 语言", ["中文", "English"])

T = LANGUAGES[st.session_state.lang]

# --- Login ---
if not st.session_state.user:
    st.markdown(f"""
    <div style='background-color: #1E1E1E; padding: 30px; border-radius: 15px; border: 1px solid #333; box-shadow: 0 4px 15px rgba(0,0,0,0.5); max-width: 500px; margin: auto;'>
        <h2 style='text-align: center; color: #00D4FF;'>🔐 {T['title']}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("") # Spacer
        user_id = st.text_input(T['user_id'])
        password = st.text_input(T['password'], type="password")
        
        st.write("")
        if st.button(T['login_btn'], use_container_width=True):
            if not user_id or not password:
                st.warning(T['input_warn'])
            else:
                clean_id = user_id.strip().upper()
                
                # 1. Check Firewall
                is_blocked, wait_time = check_firewall(clean_id)
                if is_blocked:
                    st.error(f"⛔ FIREWALL ACTIVATED: Too many failed attempts. Please wait {wait_time} minutes.")
                    st.stop()
                
                # 2. Check Whitelist
                if clean_id not in ALLOWED_USERS:
                     log_failed_attempt(clean_id)
                     st.error(T['unauth'])
                else:
                    email = "{}@myloans.com".format(clean_id)
                    try:
                        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                        st.session_state.user = res.user
                        st.rerun()
                    except Exception as e:
                        log_failed_attempt(clean_id)
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
    # Added key for programmatic navigation
    menu = st.radio(T['menu'], [T['dashboard'], T['new_loan'], T['repayment'], T['expenses']], key='nav_menu')

# 1. Dashboard (With Financial Summary)
if menu == T['dashboard']:
    # --- Quick Menu for Mobile ---
    st.markdown("### 📱 快速导航 (Quick Menu)")
    c_nav1, c_nav2, c_nav3 = st.columns(3)
    c_nav1.button(T['new_loan'], key="nav_home_new", on_click=navigate_to, args=(T['new_loan'],))
    c_nav2.button(T['repayment'], key="nav_home_repay", on_click=navigate_to, args=(T['repayment'],))
    c_nav3.button(T['expenses'], key="nav_home_exp", on_click=navigate_to, args=(T['expenses'],))
    
    st.divider()
    
    st.subheader(T['overview'])
    
    # --- Financial Summary (Monthly) ---
    st.markdown("#### " + T['fin_summary'])
    try:
        now = datetime.now()
        first_day = now.replace(day=1).isoformat()
        
        # 1. Fetch Repayments this month (Income, Interest, Penalty)
        rep_res = supabase.table("repayments").select("*").gte("created_at", first_day).execute()
        df_rep = pd.DataFrame(rep_res.data) if rep_res.data else pd.DataFrame(columns=["amount_paid", "interest_part", "is_penalty", "penalty_amount"])
        
        # Check if columns exist (for backward compatibility or new tables)
        if "is_penalty" not in df_rep.columns: df_rep["is_penalty"] = False
        if "penalty_amount" not in df_rep.columns: df_rep["penalty_amount"] = 0.0
        
        total_income = df_rep["amount_paid"].sum()
        total_int = df_rep["interest_part"].sum()
        # Penalty is tricky: if is_penalty=True, amount_paid is penalty. OR we track penalty_amount separately.
        # Assuming is_penalty=True means the whole amount is penalty.
        total_penalty = df_rep[df_rep["is_penalty"] == True]["amount_paid"].sum()
        
        # 2. Fetch Loans this month (Loaned Out)
        loan_res = supabase.table("loans").select("*").gte("created_at", first_day).execute()
        df_loans = pd.DataFrame(loan_res.data) if loan_res.data else pd.DataFrame(columns=["loan_amount"])
        total_loaned = df_loans["loan_amount"].sum()
        
        # 3. Fetch Expenses this month
        exp_res = supabase.table("expenses").select("*").gte("created_at", first_day).execute()
        df_exp = pd.DataFrame(exp_res.data) if exp_res.data else pd.DataFrame(columns=["amount"])
        total_exp = df_exp["amount"].sum()
        
        # 4. Profit
        # Profit = Interest + Penalty - Expenses (Simple view)
        # OR Profit = Income - Expenses (Cash flow view) - User asked for "Total Profit" usually implies Net Income.
        # Let's use: (Interest + Penalty) - Expenses
        total_profit = (total_int + total_penalty) - total_exp
        
        # Display Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric(T['total_income'], "{:,.2f}".format(total_income))
        m2.metric(T['total_loaned'], "{:,.2f}".format(total_loaned))
        m3.metric(T['total_int'], "{:,.2f}".format(total_int))
        
        m4, m5, m6 = st.columns(3)
        m4.metric(T['total_penalty'], "{:,.2f}".format(total_penalty))
        m5.metric(T['total_exp'], "{:,.2f}".format(total_exp))
        # Fixed Key Error here
        m6.metric(T['net_profit'], "{:,.2f}".format(total_profit))
        
        st.markdown("### 📊 " + T['overview'])
        chart_data = pd.DataFrame({
            "Category": [T['total_income'], T['total_loaned'], T['total_exp'], T['net_profit']],
            "Amount": [total_income, total_loaned, total_exp, total_profit]
        })
        st.bar_chart(chart_data.set_index("Category"))
        
        st.divider()
        
    except Exception as e:
        st.error("Error loading summary: " + str(e))

    try:
        # Load Loans
        res = supabase.table("loans").select("*").neq("status", "Deleted").execute() # Filter deleted
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
    # Back Button
    st.button("🔙 返回菜单 (Menu)", key='back_new_loan', on_click=navigate_to, args=(T['dashboard'],))
        
    st.subheader(T['add_customer'])
    with st.form("add"):
        c1, c2 = st.columns(2)
        name = c1.text_input(T['name'])
        phone = c2.text_input(T['phone']) # New: Phone
        
        c3, c4 = st.columns(2)
        ic = c3.text_input(T['ic'])
        
        c_amt, c_fee = st.columns(2)
        amt = c_amt.number_input(T['amount'], min_value=0.0)
        fee = c_fee.number_input(T['fee'], min_value=0.0)
        
        c_int, c_get = st.columns(2)
        interest = c_int.number_input(T['interest'], min_value=0.0)
        actual_get = amt - fee
        c_get.metric(T['actual_get'], actual_get)
        
        # New: Remark for "Actual Get / Repay"
        loan_remark = st.text_input(T['loan_remark'], value="Actual: {}, Repay: {}".format(actual_get, amt))
        
        method = st.selectbox(T['repay_method'], [T['weekly'], T['monthly']])
        repay_remark = st.text_input(T['repay_remark']) # New: Repay Remark
        
        c7, c8 = st.columns(2)
        who = c7.text_input(T['who'])
        account = c8.text_input(T['account'])
        
        if st.form_submit_button(T['submit']):
            try:
                # Calculate Next Due Date
                now = datetime.now()
                if method == T['weekly'] or method == "Weekly" or method == "按周":
                    next_due = now + timedelta(days=7)
                else:
                    next_due = now + timedelta(days=30)
                    
                data = {
                    "name": name, 
                    "phone": phone,
                    "ic": ic, 
                    "loan_amount": amt, 
                    "fee": fee,
                    "interest": interest,
                    "actual_get": actual_get, 
                    "balance": amt, 
                    "repay_method": method,
                    "who_issued": who,
                    "account_no": account,
                    "loan_remark": loan_remark,
                    "repay_remark": repay_remark,
                    "next_due_date": next_due.date().isoformat(),
                    "created_at": datetime.now().isoformat(),
                    "status": "Active"
                }
                supabase.table("loans").insert(data).execute()
                st.success(T['saved'].format(name))
            except Exception as e:
                st.error(T['save_fail'].format(e))

# 3. Repayment (Updated with Daily Due & Overdue)
elif menu == T['repayment']:
    # Back Button
    st.button("🔙 返回菜单 (Menu)", key='back_repay', on_click=navigate_to, args=(T['dashboard'],))
        
    st.subheader(T['repayment'])
    
    # --- A. Daily Due & Overdue Section ---
    st.markdown("### 📅 Status")
    try:
        # Fetch Active Loans
        res = supabase.table("loans").select("*").neq("status", "Deleted").gt("balance", 0).execute()
        active_loans = res.data if res.data else []
        
        today = datetime.now().date()
        
        col_due, col_over = st.columns(2)
        
        # 1. Due Today
        with col_due:
            st.markdown("#### " + T['due_today'])
            for l in active_loans:
                if l.get('next_due_date') == today.isoformat():
                    c_d1, c_d2 = st.columns([3, 1])
                    c_d1.info(f"{l['name']} (${l['balance']})")
                    if c_d2.button(T['mark_paid'], key=f"pay_{l['id']}"):
                         st.session_state['quick_pay_id'] = l['id'] # Store for form below
            
        # 2. Overdue (Past 12am check effectively means date < today)
        with col_over:
            st.markdown("#### " + T['overdue'])
            for l in active_loans:
                due_date_str = l.get('next_due_date')
                if due_date_str:
                    due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
                    if due_date < today:
                        days_late = (today - due_date).days
                        st.error(f"{l['name']} - {days_late} {T['days_overdue']}")
                        
                        # Add Penalty UI
                        with st.expander(T['add_penalty']):
                            pen_amt = st.number_input(T['penalty_amt'], key=f"pen_{l['id']}", min_value=0.0, step=10.0)
                            if st.button(T['submit'], key=f"btn_pen_{l['id']}"):
                                # Update Loan (Add penalty to balance & overdue_penalty field)
                                new_bal = l['balance'] + pen_amt
                                new_pen = (l.get('overdue_penalty') or 0) + pen_amt
                                supabase.table("loans").update({"balance": new_bal, "overdue_penalty": new_pen}).eq("id", l['id']).execute()
                                # Record as Repayment (Type: Penalty) or just a Penalty Record? 
                                # Usually penalty increases balance. Payment decreases it.
                                # Let's just record it in repayments as a "Penalty Charge" (negative payment? No, just track it).
                                # Actually, user said "Add Penalty". I added it to balance.
                                st.success(T['penalty_added'])
                                st.rerun()

    except Exception as e:
        st.error("Error checking due dates: " + str(e))
        
    st.divider()

    # --- B. Normal Repayment Form ---
    if not active_loans:
        st.info("No active loans found.")
    else:
        # Pre-select if quick pay was clicked
        loan_options = {"{} (Bal: {})".format(l['name'], l['balance']): l for l in active_loans}
        
        # Find index of quick_pay_id
        index = 0
        if 'quick_pay_id' in st.session_state:
            for i, (k, v) in enumerate(loan_options.items()):
                if v['id'] == st.session_state['quick_pay_id']:
                    index = i
                    break
        
        selected_label = st.selectbox(T['select_cust'], list(loan_options.keys()), index=index)
        selected_loan = loan_options[selected_label]
        
        with st.form("repay"):
            st.markdown(f"**{selected_loan['name']}** - {selected_loan.get('repay_remark', '')}")
            
            c1, c2 = st.columns(2)
            total_paid = c1.number_input(T['total_paid'], min_value=0.0)
            handler = c2.text_input(T['handler'], value=user_name)
            
            c3, c4 = st.columns(2)
            deduct_int = c3.number_input(T['deduct_int'], min_value=0.0)
            deduct_prin = c4.number_input(T['deduct_prin'], min_value=0.0)
            
            # Next Due Date Update
            next_due_update = st.checkbox("Update Next Due Date?", value=True)
            
            # Delete Option
            delete_user = st.checkbox(T['delete_loan'])
            
            if st.form_submit_button(T['submit']):
                if delete_user:
                    # Soft Delete
                    supabase.table("loans").update({"status": "Deleted"}).eq("id", selected_loan['id']).execute()
                    st.warning(T['deleted'])
                    st.rerun()
                else:
                    new_balance = selected_loan['balance'] - deduct_prin
                    
                    # 1. Update Loan Balance & Next Due
                    update_data = {"balance": new_balance}
                    if next_due_update:
                        # Add 7 days or 30 days based on method
                        current_due_str = selected_loan.get('next_due_date')
                        if current_due_str:
                            current_due = datetime.strptime(current_due_str, "%Y-%m-%d")
                            method = selected_loan.get('repay_method', '')
                            if "Week" in method or "周" in method:
                                new_due = current_due + timedelta(days=7)
                            else:
                                new_due = current_due + timedelta(days=30)
                            update_data["next_due_date"] = new_due.date().isoformat()
                            
                    supabase.table("loans").update(update_data).eq("id", selected_loan['id']).execute()
                    
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
                    if 'quick_pay_id' in st.session_state: del st.session_state['quick_pay_id']
                    st.rerun()

# 4. Expenses
elif menu == T['expenses']:
    # Back Button
    st.button("🔙 返回菜单 (Menu)", key='back_exp', on_click=navigate_to, args=(T['dashboard'],))
        
    st.subheader(T['expenses'])
    with st.form("exp"):
        category = st.text_input(T['exp_cat']) 
        # Removed "Select Customer" as requested
        # customer = st.text_input(T['select_cust'] + " (Optional)") 
        
        amount = st.number_input(T['exp_amt'], min_value=0.0)
        handler = st.text_input(T['handler'], value=user_name)
        remark = st.text_area(T['exp_remark'])
        
        if st.form_submit_button(T['submit']):
            exp_data = {
                "category": category,
                # "customer_name": customer, # Removed
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
