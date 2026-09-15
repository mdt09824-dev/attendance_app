import os
import sqlite3
import pandas as pd
from datetime import datetime
import streamlit as st

DEFAULT_STUDENTS = [
    "Rounak", "Nirob", "Jahidul", "Abir", "Tafin",
    "Anik", "Muhin", "Mehedi", "Alif", "Samia",
    "Sorna", "Tuli", "Tabassum", "Sumaiya", "Bonna",
    "Runa", "Maria"
]

INITIAL_FINE = {
    "Tabassum": 20,
    "Runa": 20
}

DB_FILE = "attendance_pro.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (name TEXT PRIMARY KEY, phone TEXT, email TEXT, parent_phone TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (date TEXT, student_name TEXT, status TEXT, PRIMARY KEY (date, student_name))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS payments (student_name TEXT PRIMARY KEY, paid_amount REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS initial_fines (student_name TEXT PRIMARY KEY, amount REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS fine_settings (key TEXT PRIMARY KEY, value TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, action TEXT)''')
    
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        for s in DEFAULT_STUDENTS:
            cursor.execute("INSERT OR IGNORE INTO students (name, phone, email, parent_phone) VALUES (?, ?, ?, ?)", (s, "01700000000", "student@gmail.com", "01800000000"))
        for s, amt in INITIAL_FINE.items():
            cursor.execute("INSERT OR REPLACE INTO initial_fines (student_name, amount) VALUES (?, ?)", (s, amt))
        cursor.execute("INSERT OR REPLACE INTO fine_settings (key, value) VALUES (?, ?)", ("regular", "20"))
        conn.commit()
    conn.close()

init_db()

st.set_page_config(page_title="Attendance Pro", page_icon="⚡", layout="centered")

# Custom Refined UI Styling (Colorful & Clean Finish)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #f8fafc; font-family: 'Inter', sans-serif; }
    
    /* Compact Neat Header */
    .hero-header {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        padding: 12px 20px;
        border-radius: 12px;
        color: white;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.25);
        margin-bottom: 15px;
        text-align: center;
    }
    .hero-header h1 { margin: 0; font-size: 20px; font-weight: 700; }
    .hero-header p { margin: 2px 0 0 0; opacity: 0.85; font-size: 11px; }

    /* Metric Cards */
    .metric-container {
        display: flex;
        gap: 8px;
        margin-bottom: 15px;
    }
    .metric-box {
        flex: 1;
        background: #1e293b;
        border: 1px solid #334155;
        padding: 10px 5px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .metric-box h4 { margin: 0; font-size: 10px; color: #94a3b8; text-transform: uppercase; }
    .metric-box h2 { margin: 4px 0 0 0; font-size: 16px; color: #f8fafc; font-weight: 700; }

    /* Student Row Card */
    .student-row {
        background: #1e293b;
        border: 1px solid #334155;
        padding: 10px 14px;
        border-radius: 10px;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* Rounded Colorful Buttons */
    .stButton button {
        width: 100% !important;
        border-radius: 20px !important;
        font-weight: 600 !important;
        font-size: 12px !important;
        padding: 6px 10px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        transition: all 0.2s ease;
    }
    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }

    /* Table & Dataframe Styling */
    div[data-testid="stDataFrame"] {
        background: #1e293b;
        border-radius: 10px;
        padding: 5px;
        border: 1px solid #334155;
    }
    </style>
""", unsafe_allow_html=True)

def today_str():
    return datetime.now().strftime("%Y-%m-%d")

def log_action(action):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO logs (timestamp, action) VALUES (?, ?)", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), action))
    conn.commit()
    conn.close()

def get_students():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM students")
    rows = cursor.fetchall()
    conn.close()
    return [row["name"] for row in rows]

def get_day_attendance(date_str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT student_name, status FROM attendance WHERE date = ?", (date_str,))
    rows = cursor.fetchall()
    conn.close()
    return {row["student_name"]: row["status"] for row in rows}

def save_attendance(date_str, student_name, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO attendance (date, student_name, status) VALUES (?, ?, ?)
        ON CONFLICT(date, student_name) DO UPDATE SET status = ?
    ''', (date_str, student_name, status, status))
    conn.commit()
    conn.close()

def get_payments():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT student_name, paid_amount FROM payments")
    rows = cursor.fetchall()
    conn.close()
    return {row["student_name"]: row["paid_amount"] for row in rows}

def get_initial_fines():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT student_name, amount FROM initial_fines")
    rows = cursor.fetchall()
    conn.close()
    return {row["student_name"]: row["amount"] for row in rows}

def get_fine_settings():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM fine_settings")
    rows = cursor.fetchall()
    conn.close()
    settings = {"regular": 20, "special_dates": {}}
    for row in rows:
        if row["key"] == "regular":
            settings["regular"] = int(row["value"])
    return settings

def get_current_fines():
    students = get_students()
    initial_fines = get_initial_fines()
    settings = get_fine_settings()
    regular_fine = settings.get("regular", 20)
    
    fines = {s: int(initial_fines.get(s, 0)) for s in students}
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT date, student_name FROM attendance WHERE status = 'ABSENT'")
    absent_records = cursor.fetchall()
    conn.close()
    
    for row in absent_records:
        student = row["student_name"]
        if student in fines:
            fines[student] += regular_fine
            
    payments = get_payments()
    net_fines = {}
    for s in students:
        net_fines[s] = max(0, fines.get(s, 0) - payments.get(s, 0))
    return net_fines, fines

students = get_students()

# Sidebar / Menu Navigation Options (Integrated cleanly)
with st.sidebar:
    st.markdown("### ⚙️ Menu & Options")
    nav_mode = st.selectbox("Select Function", [
        "1. Daily Attendance Dashboard",
        "2. Financial Ledger & Dues",
        "3. Fee Collection Gateway",
        "4. Attendance History Logs",
        "5. Member Management",
        "6. Fine Settings & Rules",
        "7. System Reset"
    ])

# Compact Title Banner
st.markdown("""
    <div class="hero-header">
        <h1>⚡ Attendance E-Khata Pro</h1>
        <p>Smart Student Attendance & Fee Management</p>
    </div>
""", unsafe_allow_html=True)

selected_date = st.date_input("Select Date", datetime.strptime(today_str(), "%Y-%m-%d"))
current_date = selected_date.strftime("%Y-%m-%d")

# 1. Daily Attendance Dashboard
if nav_mode == "1. Daily Attendance Dashboard":
    day_data = get_day_attendance(current_date)
    present = sum(1 for s in students if day_data.get(s) == "PRESENT")
    leave = sum(1 for s in students if day_data.get(s) == "LEAVE")
    absent = sum(1 for s in students if day_data.get(s) == "ABSENT")
    net_fines, _ = get_current_fines()
    
    st.markdown(f"""
        <div class="metric-container">
            <div class="metric-box"><h4>Present</h4><h2>{present}</h2></div>
            <div class="metric-box"><h4>Leave</h4><h2>{leave}</h2></div>
            <div class="metric-box"><h4>Absent</h4><h2>{absent}</h2></div>
            <div class="metric-box"><h4>Total Due</h4><h2>{sum(net_fines.values())} Tk</h2></div>
        </div>
    """, unsafe_allow_html=True)
    
    # Quick Bulk Action Buttons
    c1, c2 = st.columns(2)
    if c1.button("✔️ Select All Present"):
        for s in students: save_attendance(current_date, s, "PRESENT")
        st.success("All marked present!"); st.rerun()
    if c2.button("👤 Select All Leave"):
        for s in students: save_attendance(current_date, s, "LEAVE")
        st.success("All marked leave!"); st.rerun()
        
    st.markdown("---")
    
    for student in students:
        status = day_data.get(student, "Not Set")
        badge_color = "#334155"
        if status == "PRESENT": badge_color = "#065f46"
        elif status == "LEAVE": badge_color = "#92400e"
        elif status == "ABSENT": badge_color = "#991b1b"
        
        st.markdown(f"""
            <div class='student-row'>
                <span style='font-weight:600; font-size:14px;'>👤 {student}</span>
                <span style='padding:3px 10px; border-radius:12px; font-size:10px; font-weight:700; background:{badge_color}; color:white;'>{status}</span>
            </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(3)
        if cols[0].button("✔️ Present", key=f"p_{student}"): 
            save_attendance(current_date, student, "PRESENT"); st.rerun()
        if cols[1].button("👤 Leave", key=f"l_{student}"): 
            save_attendance(current_date, student, "LEAVE"); st.rerun()
        if cols[2].button("❌ Absent", key=f"a_{student}"): 
            save_attendance(current_date, student, "ABSENT"); st.rerun()

# 2. Financial Ledger & Dues
elif nav_mode == "2. Financial Ledger & Dues":
    st.markdown("### 💰 Financial Ledger & Fine Breakdown")
    net_fines, gross_fines = get_current_fines()
    payments = get_payments()
    data = [{"Name": s, "Total Fine": f"{gross_fines.get(s,0)} Tk", "Paid": f"{payments.get(s,0)} Tk", "Due": f"{net_fines.get(s,0)} Tk"} for s in students]
    st.dataframe(pd.DataFrame(data), use_container_width=True)

# 3. Fee Collection Gateway
elif nav_mode == "3. Fee Collection Gateway":
    st.markdown("### 💵 Secure Fee Collection Portal")
    net_fines, _ = get_current_fines()
    sel_s = st.selectbox("Select Student", students)
    due = net_fines.get(sel_s, 0)
    st.info(f"Outstanding Due for {sel_s}: **{due} Taka**")
    amt = st.number_input("Enter Amount Collected (Tk)", min_value=0, step=10)
    if st.button("Confirm Collection"):
        if amt > 0:
            payments = get_payments()
            new_p = payments.get(sel_s, 0) + amt
            conn = get_db_connection()
            conn.cursor().execute("INSERT INTO payments (student_name, paid_amount) VALUES (?, ?) ON CONFLICT(student_name) DO UPDATE SET paid_amount = ?", (sel_s, new_p, new_p))
            conn.commit(); conn.close()
            log_action(f"Collected {amt} Tk from {sel_s}")
            st.success("Payment recorded successfully!"); st.rerun()

# 4. Attendance History Logs
elif nav_mode == "4. Attendance History Logs":
    st.markdown("### 📊 Historical Attendance Records")
    conn = get_db_connection()
    dates = [r["date"] for r in conn.cursor().execute("SELECT DISTINCT date FROM attendance ORDER BY date DESC").fetchall()]
    conn.close()
    if dates:
        chosen = st.selectbox("Select History Date", dates)
        day_data = get_day_attendance(chosen)
        df = pd.DataFrame([{"Student Name": s, "Status": day_data.get(s, "Not Set")} for s in students])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No historical records available.")

# 5. Member Management
elif nav_mode == "5. Member Management":
    st.markdown("### 👥 Student Directory & Members")
    new_s = st.text_input("New Member Full Name")
    if st.button("Register Student"):
        if new_s and new_s not in students:
            conn = get_db_connection()
            conn.cursor().execute("INSERT INTO students (name) VALUES (?)", (new_s,))
            conn.commit(); conn.close()
            st.success(f"Added {new_s} successfully!"); st.rerun()

# 6. Fine Settings & Rules
elif nav_mode == "6. Fine Settings & Rules":
    st.markdown("### ⚙️ Fine Configuration")
    settings = get_fine_settings()
    reg = st.number_input("Absent Fine Amount (Taka)", value=settings.get("regular", 20))
    if st.button("Save Settings"):
        conn = get_db_connection()
        conn.cursor().execute("INSERT OR REPLACE INTO fine_settings (key, value) VALUES ('regular', ?)", (str(reg),))
        conn.commit(); conn.close()
        st.success("Fine rules updated!")

# 7. System Reset
elif nav_mode == "7. System Reset":
    st.markdown("### ⚠️ Factory Reset Center")
    if st.button("Reset Entire Application"):
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        init_db()
        st.success("System reset complete!"); st.rerun()
