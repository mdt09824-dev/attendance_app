import os
import sqlite3
from datetime import datetime
import streamlit as st
import pandas as pd

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
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                        name TEXT PRIMARY KEY, 
                        joined_date TEXT, 
                        removed_date TEXT
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (
                        date TEXT, 
                        student_name TEXT, 
                        status TEXT, 
                        PRIMARY KEY (date, student_name)
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS payments (
                        student_name TEXT PRIMARY KEY, 
                        paid_amount REAL
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS initial_fines (
                        student_name TEXT PRIMARY KEY, 
                        amount REAL
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS fine_settings (
                        key TEXT PRIMARY KEY, 
                        value TEXT
                    )''')
    
    conn.commit()
    
    # Check if students table is empty
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        default_join_date = "2026-01-01"
        for s in DEFAULT_STUDENTS:
            cursor.execute("INSERT OR IGNORE INTO students (name, joined_date, removed_date) VALUES (?, ?, ?)", (s, default_join_date, None))
        for s, amt in INITIAL_FINE.items():
            cursor.execute("INSERT OR REPLACE INTO initial_fines (student_name, amount) VALUES (?, ?)", (s, amt))
        cursor.execute("INSERT OR REPLACE INTO fine_settings (key, value) VALUES (?, ?)", ("regular", "20"))
        conn.commit()
    conn.close()

init_db()

st.set_page_config(page_title="Attendance E-Khata Pro", page_icon="⚡", layout="centered")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #f8fafc; font-family: 'Inter', sans-serif; }
    
    .hero-header {
        background: linear-gradient(135deg, #2563eb 100%, #1d4ed8 0%);
        padding: 16px 20px;
        border-radius: 14px;
        color: white;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
        margin-bottom: 15px;
        text-align: center;
    }
    .hero-header h1 { margin: 0; font-size: 22px; font-weight: 700; letter-spacing: 0.3px; }
    .hero-header p { margin: 4px 0 0 0; opacity: 0.95; font-size: 12px; font-weight: 500; }

    .metric-container {
        display: flex;
        gap: 8px;
        margin-bottom: 12px;
        width: 100%;
    }
    .metric-box-present {
        flex: 1; background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        padding: 12px 6px; border-radius: 12px; text-align: center; color: white; box-shadow: 0 3px 8px rgba(16, 185, 129, 0.25);
    }
    .metric-box-leave {
        flex: 1; background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        padding: 12px 6px; border-radius: 12px; text-align: center; color: white; box-shadow: 0 3px 8px rgba(245, 158, 11, 0.25);
    }
    .metric-box-absent {
        flex: 1; background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        padding: 12px 6px; border-radius: 12px; text-align: center; color: white; box-shadow: 0 3px 8px rgba(239, 68, 68, 0.25);
    }
    .metric-box-due {
        flex: 1; background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
        padding: 12px 6px; border-radius: 12px; text-align: center; color: white; box-shadow: 0 3px 8px rgba(6, 182, 212, 0.25);
    }
    .metric-box-present small, .metric-box-leave small, .metric-box-absent small, .metric-box-due small { font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
    .metric-box-present h3, .metric-box-leave h3, .metric-box-absent h3, .metric-box-due h3 { margin: 4px 0 0 0; font-size: 16px; font-weight: 800; }

    .student-row {
        background: #1e293b;
        border: 1px solid #334155;
        padding: 10px 14px;
        border-radius: 10px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .stButton button {
        width: 100% !important;
        border-radius: 20px !important;
        font-weight: 600 !important;
        font-size: 12px !important;
        padding: 6px 10px !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        transition: all 0.2s ease;
    }
    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }

    div[data-testid="stDataFrame"] {
        background: #1e293b;
        border-radius: 10px;
        padding: 6px;
        border: 1px solid #334155;
    }
    </style>
""", unsafe_allow_html=True)

def today_str():
    return datetime.now().strftime("%Y-%m-%d")

def format_date(d_str):
    try:
        return datetime.strptime(d_str, "%Y-%m-%d").strftime("%d-%m-%Y")
    except:
        return d_str

def get_active_students_for_date(date_str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, joined_date, removed_date FROM students")
    rows = cursor.fetchall()
    conn.close()
    
    active = []
    for row in rows:
        name = row["name"]
        joined = row["joined_date"] or "2026-01-01"
        removed = row["removed_date"]
        
        # Check if student was active on this specific date
        if date_str >= joined and (removed is None or date_str <= removed):
            active.append(name)
    return active

def get_all_students_ever():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, joined_date, removed_date FROM students")
    rows = cursor.fetchall()
    conn.close()
    return rows

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
        key = row["key"]
        val = row["value"]
        if key == "regular":
            try:
                settings["regular"] = int(val)
            except:
                settings["regular"] = 20
        elif key.startswith("spec_"):
            spec_date = key.replace("spec_", "")
            try:
                settings["special_dates"][spec_date] = int(val)
            except:
                pass
    return settings

def get_current_fines():
    all_students_info = get_all_students_ever()
    all_names = [r["name"] for r in all_students_info]
    initial_fines = get_initial_fines()
    settings = get_fine_settings()
    regular_fine = settings.get("regular", 20)
    special_dates = settings.get("special_dates", {})
    
    fines = {s: int(initial_fines.get(s, 0)) for s in all_names}
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT date, student_name FROM attendance WHERE status = 'ABSENT'")
    absent_records = cursor.fetchall()
    conn.close()
    
    for row in absent_records:
        d_str = row["date"]
        student = row["student_name"]
        day_fine = special_dates.get(d_str, regular_fine)
        if student in fines:
            fines[student] += day_fine
            
    payments = get_payments()
    net_fines = {}
    for s in all_names:
        net_fines[s] = max(0, fines.get(s, 0) - payments.get(s, 0))
    return net_fines, fines

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

st.markdown("""
    <div class="hero-header">
        <h1>📚 Attendance E-Khata Pro</h1>
        <p>⚡ Track &nbsp;•&nbsp; Manage &nbsp;•&nbsp; Build Better Future</p>
    </div>
""", unsafe_allow_html=True)

selected_date = st.date_input("Select Date", datetime.strptime(today_str(), "%Y-%m-%d"))
current_date = selected_date.strftime("%Y-%m-%d")
active_students = get_active_students_for_date(current_date)

if nav_mode == "1. Daily Attendance Dashboard":
    day_data = get_day_attendance(current_date)
    present = sum(1 for s in active_students if day_data.get(s) == "PRESENT")
    leave = sum(1 for s in active_students if day_data.get(s) == "LEAVE")
    absent = sum(1 for s in active_students if day_data.get(s) == "ABSENT")
    net_fines, _ = get_current_fines()
    total_due_sum = sum(net_fines.values())
    
    st.markdown(f"""
        <div class="metric-container">
            <div class="metric-box-present"><small>Present</small><h3>{present}</h3></div>
            <div class="metric-box-leave"><small>Leave</small><h3>{leave}</h3></div>
            <div class="metric-box-absent"><small>Absent</small><h3>{absent}</h3></div>
            <div class="metric-box-due"><small>Total Due</small><h3>{total_due_sum}Tk</h3></div>
        </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    if c1.button("✔️ Select All Present"):
        for s in active_students: 
            save_attendance(current_date, s, "PRESENT")
        st.success("✨ সফলভাবে সবাইকেই 'Present' হিসেবে মার্ক করা হয়েছে!")
        st.rerun()
    if c2.button("👤 Select All Leave"):
        for s in active_students: 
            save_attendance(current_date, s, "LEAVE")
        st.success("✨ সফলভাবে সবাইকেই 'Leave' হিসেবে মার্ক করা হয়েছে!")
        st.rerun()
        
    st.markdown("---")
    
    for student in active_students:
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
            save_attendance(current_date, student, "PRESENT")
            st.success(f"✨ সফল হয়েছে: {student}-এর উপস্থিতি সেভ করা হয়েছে!")
            st.rerun()
        if cols[1].button("👤 Leave", key=f"l_{student}"): 
            save_attendance(current_date, student, "LEAVE")
            st.success(f"✨ সফল হয়েছে: {student}-এর ছুটি সেভ করা হয়েছে!")
            st.rerun()
        if cols[2].button("❌ Absent", key=f"a_{student}"): 
            save_attendance(current_date, student, "ABSENT")
            st.success(f"✨ সফল হয়েছে: {student}-এর অনুপস্থিতি সেভ করা হয়েছে!")
            st.rerun()

elif nav_mode == "2. Financial Ledger & Dues":
    st.markdown("### 💰 Financial Ledger & Fine Breakdown")
    net_fines, gross_fines = get_current_fines()
    payments = get_payments()
    all_info = get_all_students_ever()
    
    data = []
    for info in all_info:
        s = info["name"]
        display_name = f"{s} ❌" if info["removed_date"] else s
        data.append({
            "Name": display_name,
            "Total Fine": f"{gross_fines.get(s,0)} Tk",
            "Paid": f"{payments.get(s,0)} Tk",
            "Due": f"{net_fines.get(s,0)} Tk"
        })
    st.dataframe(pd.DataFrame(data), use_container_width=True)

elif nav_mode == "3. Fee Collection Gateway":
    st.markdown("### 💵 Secure Fee Collection Portal")
    net_fines, _ = get_current_fines()
    all_info = get_all_students_ever()
    all_names = [i["name"] for i in all_info]
    
    sel_s = st.selectbox("Select Student", all_names)
    due = net_fines.get(sel_s, 0)
    st.info(f"Outstanding Due for {sel_s}: **{due} Taka**")
    amt = st.number_input("Enter Amount Collected (Tk)", min_value=0, step=10)
    if st.button("Confirm Collection"):
        if amt > 0:
            payments = get_payments()
            new_p = payments.get(sel_s, 0) + amt
            conn = get_db_connection()
            conn.cursor().execute("INSERT INTO payments (student_name, paid_amount) VALUES (?, ?) ON CONFLICT(student_name) DO UPDATE SET paid_amount = ?", (sel_s, new_p, new_p))
            conn.commit()
            conn.close()
            st.success(f"🎉 সফল হয়েছে! {sel_s}-এর কাছ থেকে {amt} Tk ফি সফলভাবে সংগ্রহ ও আপডেট করা হয়েছে।")
            st.rerun()
        else:
            st.warning("দয়া করে সঠিক পরিমাণ টাকা লিখুন।")

elif nav_mode == "4. Attendance History Logs":
    st.markdown("### 📊 Historical Attendance Records & Presence Count")
    conn = get_db_connection()
    dates = [r["date"] for r in conn.cursor().execute("SELECT DISTINCT date FROM attendance ORDER BY date DESC").fetchall()]
    conn.close()
    
    if dates:
        chosen = st.selectbox("Select History Date", dates)
        day_data = get_day_attendance(chosen)
        active_on_day = get_active_students_for_date(chosen)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT student_name, COUNT(*) as days_present FROM attendance WHERE status = 'PRESENT' GROUP BY student_name")
        present_counts = {row["student_name"]: row["days_present"] for row in cursor.fetchall()}
        conn.close()
        
        df_list = []
        for s in active_on_day:
            df_list.append({
                "Student Name": s,
                "Status": day_data.get(s, "Not Set"),
                "Total Days Present": present_counts.get(s, 0)
            })
        st.dataframe(pd.DataFrame(df_list), use_container_width=True)
    else:
        st.info("কোনো হিস্টোরিক্যাল রেকর্ড পাওয়া যায়নি।")

elif nav_mode == "5. Member Management":
    st.markdown("### 👥 Student Directory & Members")
    
    tab1, tab2 = st.tabs(["➕ Add Member", "❌ Remove Member"])
    
    with tab1:
        new_s = st.text_input("New Member Full Name")
        if st.button("Register Student"):
            if new_s:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM students WHERE name = ?", (new_s,))
                exists = cursor.fetchone()
                if exists:
                    cursor.execute("UPDATE students SET removed_date = NULL WHERE name = ?", (new_s,))
                else:
                    cursor.execute("INSERT INTO students (name, joined_date, removed_date) VALUES (?, ?, ?)", (new_s, today_str(), None))
                conn.commit()
                conn.close()
                st.success(f"🎉 সফল হয়েছে! নতুন শিক্ষার্থী '{new_s}' সফলভাবে যুক্ত হয়েছে।")
                st.rerun()
            else:
                st.warning("দয়া করে শিক্ষার্থীর নাম লিখুন।")
                
    with tab2:
        all_info = get_all_students_ever()
        active_names = [i["name"] for i in all_info if i["removed_date"] is None]
        rem_s = st.selectbox("Select Student to Remove", active_names if active_names else ["No active students"])
        if st.button("Confirm Removal") and active_names:
            conn = get_db_connection()
            conn.cursor().execute("UPDATE students SET removed_date = ? WHERE name = ?", (today_str(), rem_s))
            conn.commit()
            conn.close()
            st.success(f"✨ সফল হয়েছে! শিক্ষার্থী '{rem_s}' কে তালিকা থেকে অব্যাহতি দেওয়া হয়েছে এবং নামের সাথে ক্রস যুক্ত করা হয়েছে।")
            st.rerun()

elif nav_mode == "6. Fine Settings & Rules":
    st.markdown("### ⚙️ Fine Configuration & Special Dates")
    settings = get_fine_settings()
    reg = st.number_input("Absent Fine Amount (Taka)", value=settings.get("regular", 20))
    
    st.markdown("#### বিশেষ দিন বা পরীক্ষার দিনের ফাইন")
    spec_date_input = st.date_input("Select Special Date", datetime.strptime(today_str(), "%Y-%m-%d"))
    spec_date_str = spec_date_input.strftime("%Y-%m-%d")
    existing_spec_fine = settings["special_dates"].get(spec_date_str, 30)
    spec_fine_val = st.number_input(f"Fine for {format_date(spec_date_str)} (Taka)", value=int(existing_spec_fine))
    
    if st.button("Save Settings"):
        settings["special_dates"][spec_date_str] = spec_fine_val
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO fine_settings (key, value) VALUES ('regular', ?)", (str(reg),))
        for d, amt in settings["special_dates"].items():
            cursor.execute("INSERT OR REPLACE INTO fine_settings (key, value) VALUES (?, ?)", (f"spec_{d}", str(amt)))
        conn.commit()
        conn.close()
        st.success("🎉 সফল হয়েছে! ফাইন সেটিংস এবং বিশেষ দিনের নিয়ম সফলভাবে সেভ ও আপডেট হয়েছে।")
        st.rerun()

elif nav_mode == "7. System Reset":
    st.markdown("### ⚠️ Factory Reset Center")
    st.warning("সতর্কতা: রিসেট করলে ডাটাবেস সম্পূর্ণ মুছে যাবে।")
    if st.button("Reset Entire Application"):
        if os.path.exists(DB_FILE): 
            os.remove(DB_FILE)
        init_db()
        st.success("✨ সফলভাবে সিস্টেম রিসেট করা হয়েছে!")
        st.rerun()
