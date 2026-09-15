import os
import sqlite3
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

# SQLite Database Setup
DB_FILE = "attendance_ekhata.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Students Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            name TEXT PRIMARY KEY
        )
    ''')
    
    # Days / Attendance Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            date TEXT,
            student_name TEXT,
            status TEXT,
            PRIMARY KEY (date, student_name)
        )
    ''')
    
    # Payments Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            student_name TEXT PRIMARY KEY,
            paid_amount REAL
        )
    ''')
    
    # Initial Fines Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS initial_fines (
            student_name TEXT PRIMARY KEY,
            amount REAL
        )
    ''')
    
    # Fine Settings Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fine_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    conn.commit()
    
    # Initialize default data if tables are empty
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        for s in DEFAULT_STUDENTS:
            cursor.execute("INSERT OR IGNORE INTO students (name) VALUES (?)", (s,))
        
        for s, amt in INITIAL_FINE.items():
            cursor.execute("INSERT OR REPLACE INTO initial_fines (student_name, amount) VALUES (?, ?)", (s, amt))
            
        cursor.execute("INSERT OR REPLACE INTO fine_settings (key, value) VALUES (?, ?)", ("regular", "20"))
        conn.commit()
    
    conn.close()

# Initialize Database on Startup
init_db()

st.set_page_config(page_title="Attendance E-Khata", page_icon="📚", layout="centered")

# Custom CSS for styling
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #24292e; }
    
    .app-header {
        margin-top: 25px;
        margin-bottom: 15px;
        font-size: 28px;
        font-weight: 800;
        text-align: center;
        color: #1f2328;
        border-bottom: 2px solid #eaeef2;
        padding-bottom: 10px;
    }

    .card-container {
        display: flex;
        gap: 6px;
        margin-bottom: 10px;
    }
    .stat-card {
        flex: 1;
        padding: 6px 4px;
        border-radius: 8px;
        text-align: center;
        color: white;
        min-height: 50px;
    }
    .c-present { background-color: #2ea043; }
    .c-leave { background-color: #fb8532; }
    .c-absent { background-color: #cf222e; }
    .c-fee { background-color: #0969da; }

    .stat-card small { font-size: 10px; color: #ffffff; }
    .stat-card h4 { font-size: 13px; margin: 0; font-weight: bold; color: #ffffff; }

    .student-card-box {
        background-color: #f6f8fa;
        border: 1px solid #d0d7de;
        border-radius: 8px;
        padding: 8px 10px;
        margin-bottom: 4px;
    }

    .badge-present { background-color: #dafbe1; color: #1a7f37; border: 1px solid #2ea043; padding: 3px 8px; border-radius: 5px; font-weight: bold; font-size: 11px; }
    .badge-leave { background-color: #fff8c5; color: #9a6700; border: 1px solid #fb8532; padding: 3px 8px; border-radius: 5px; font-weight: bold; font-size: 11px; }
    .badge-absent { background-color: #ffebe9; color: #cf222e; border: 1px solid #cf222e; padding: 3px 8px; border-radius: 5px; font-weight: bold; font-size: 11px; }
    .badge-none { background-color: #eaeef2; color: #57606a; padding: 3px 8px; border-radius: 5px; font-size: 11px; }

    .stButton button {
        width: 100% !important;
        background-color: #cf222e !important;
        color: #ffdf00 !important;
        border: 1px solid #a40e17 !important;
        border-radius: 6px;
        font-weight: bold;
        font-size: 12px;
        padding: 6px 0px;
    }

    table {
        width: 100%;
        color: #24292e !important;
        background-color: #f6f8fa !important;
    }
    th {
        background-color: #eaeef2 !important;
        color: #24292e !important;
    }
    td {
        color: #24292e !important;
    }
    </style>
""", unsafe_allow_html=True)

def today_str():
    return datetime.now().strftime("%Y-%m-%d")

def format_date(d):
    try:
        return datetime.strptime(d, "%Y-%m-%d").strftime("%d-%m-%Y")
    except:
        return d

# Database Helper Functions
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

def save_attendance_db(date_str, student_name, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO attendance (date, student_name, status) VALUES (?, ?, ?)
        ON CONFLICT(date, student_name) DO UPDATE SET status = ?
    ''', (date_str, student_name, status, status))
    conn.commit()
    conn.close()

def get_fine_settings_db():
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
            settings["regular"] = int(val)
        elif key.startswith("spec_"):
            spec_date = key.replace("spec_", "")
            settings["special_dates"][spec_date] = int(val)
    return settings

def save_fine_settings_db(regular, special_dates):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO fine_settings (key, value) VALUES (?, ?)", ("regular", str(regular)))
    for d_str, amt in special_dates.items():
        cursor.execute("INSERT OR REPLACE INTO fine_settings (key, value) VALUES (?, ?)", (f"spec_{d_str}", str(amt)))
    conn.commit()
    conn.close()

def get_payments_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT student_name, paid_amount FROM payments")
    rows = cursor.fetchall()
    conn.close()
    return {row["student_name"]: row["paid_amount"] for row in rows}

def get_initial_fines_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT student_name, amount FROM initial_fines")
    rows = cursor.fetchall()
    conn.close()
    return {row["student_name"]: row["amount"] for row in rows}

def get_all_attendance_dates():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT date FROM attendance ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()
    return [row["date"] for row in rows]

def get_current_fines():
    students = get_students()
    initial_fines = get_initial_fines_db()
    fine_settings = get_fine_settings_db()
    regular_fine = fine_settings.get("regular", 20)
    special_dates = fine_settings.get("special_dates", {})

    fines = {s: int(initial_fines.get(s, 0)) for s in students}
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT date, student_name, status FROM attendance WHERE status = 'ABSENT'")
    absent_records = cursor.fetchall()
    conn.close()
    
    for row in absent_records:
        d_str = row["date"]
        student = row["student_name"]
        current_day_fine = special_dates.get(d_str, regular_fine)
        if student in fines:
            fines[student] = fines.get(student, 0) + current_day_fine
    
    payments = get_payments_db()
    net_fines = {}
    for s in students:
        total_due = fines.get(s, 0)
        paid = payments.get(s, 0)
        net_fines[s] = max(0, total_due - paid)
    return net_fines, fines

students = get_students()

# Sidebar Navigation Menu
with st.sidebar:
    st.markdown("### ☰ Navigation Menu")
    nav_mode = st.radio(
        "Menu", [
            "Dashboard", 
            "History", 
            "Total Fine", 
            "Collect Fee", 
            "Manage Members", 
            "Fine Setting", 
            "Reset"
        ], label_visibility="collapsed"
    )

# App Header
st.markdown('<div class="app-header">📚 Attendance E-Khata</div>', unsafe_allow_html=True)

# Date Selection
selected_date_obj = st.date_input(
    "Select Date", datetime.strptime(today_str(), "%Y-%m-%d")
)
current_date = selected_date_obj.strftime("%Y-%m-%d")

# ----------------- 1. DASHBOARD VIEW -----------------
if nav_mode == "Dashboard":
    day_data = get_day_attendance(current_date)

    present = sum(1 for s in students if day_data.get(s) == "PRESENT")
    leave = sum(1 for s in students if day_data.get(s) == "LEAVE")
    absent = sum(1 for s in students if day_data.get(s) == "ABSENT")
    not_set = len(students) - present - leave - absent

    net_fines, gross_fines = get_current_fines()
    total_fine_amount = sum(net_fines.values())

    st.markdown(f"""
        <div class="card-container">
            <div class="stat-card c-present">
                <small>Present</small>
                <h4>{present}</h4>
            </div>
            <div class="stat-card c-leave">
                <small>Leave</small>
                <h4>{leave}</h4>
            </div>
            <div class="stat-card c-absent">
                <small>Absent</small>
                <h4>{absent}</h4>
            </div>
            <div class="stat-card c-fee">
                <small>Total Due</small>
                <h4>{total_fine_amount}Tk</h4>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(f"**Date:** {format_date(current_date)} &nbsp;|&nbsp; **Not Set:** {not_set}")
    st.markdown("---")

    for student in students:
        current_status = day_data.get(student, "")
        
        if current_status == "PRESENT":
            status_cls = "badge-present"
            status_text = "PRESENT"
        elif current_status == "LEAVE":
            status_cls = "badge-leave"
            status_text = "LEAVE"
        elif current_status == "ABSENT":
            status_cls = "badge-absent"
            status_text = "ABSENT"
        else:
            status_cls = "badge-none"
            status_text = "-"

        with st.container():
            st.markdown(f"""
                <div class="student-card-box">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 14px; font-weight: 600; color: #24292e;">👤 {student}</span>
                        <span class="{status_cls}">{status_text}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            b_cols = st.columns(3)
            if b_cols[0].button("✔️ PRESENT", key=f"btn_p_{student}"):
                save_attendance_db(current_date, student, "PRESENT")
                st.rerun()
            if b_cols[1].button("👤 LEAVE", key=f"btn_l_{student}"):
                save_attendance_db(current_date, student, "LEAVE")
                st.rerun()
            if b_cols[2].button("❌ ABSENT", key=f"btn_a_{student}"):
                save_attendance_db(current_date, student, "ABSENT")
                st.rerun()
            st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

# ----------------- 2. HISTORY VIEW -----------------
elif nav_mode == "History":
    st.markdown("### 📅 Attendance History")
    sorted_dates = get_all_attendance_dates()

    if not sorted_dates:
        st.info("No attendance history found yet.")
    else:
        for d in sorted_dates:
            day = get_day_attendance(d)
            p = sum(1 for s in students if day.get(s) == "PRESENT")
            l = sum(1 for s in students if day.get(s) == "LEAVE")
            a = sum(1 for s in students if day.get(s) == "ABSENT")

            with st.expander(f"📅 {format_date(d)}  —  Present: {p} | Leave: {l} | Absent: {a}"):
                history_list = []
                for s in students:
                    st_val = day.get(s, "-")
                    history_list.append({
                        "Student Name": s,
                        "Status": st_val if st_val else "Not Set"
                    })
                st.table(history_list)

# ----------------- 3. TOTAL FINE VIEW -----------------
elif nav_mode == "Total Fine":
    st.markdown("### 💰 Total Due / Fine List")
    net_fines, gross_fines = get_current_fines()
    payments = get_payments_db()

    fine_data = []
    for s in students:
        tot_fine = gross_fines.get(s, 0)
        paid_amt = payments.get(s, 0)
        rem_due = net_fines.get(s, 0)
        fine_data.append({
            "Student Name": s,
            "Total Fine": f"{tot_fine} Tk",
            "Paid": f"{paid_amt} Tk",
            "Remaining Due": f"{rem_due} Tk"
        })
    st.table(fine_data)

# ----------------- 4. COLLECT FEE VIEW -----------------
elif nav_mode == "Collect Fee":
    st.markdown("### 💵 Collect Fine / Clear Dues")
    st.write("বকেয়া টাকা পরিশোধ করলে এখানে এন্ট্রি দিন, যা মোট বকেয়া থেকে স্বয়ংক্রিয়ভাবে মাইনাস হয়ে যাবে।")

    net_fines, _ = get_current_fines()
    selected_student = st.selectbox("Select Student", students)
    current_due = net_fines.get(selected_student, 0)
    
    st.info(f"Current Due for {selected_student}: **{current_due} Taka**")
    pay_amount = st.number_input("Enter Amount to Pay (Taka)", min_value=0, step=10)

    if st.button("Confirm Payment"):
        if pay_amount > 0:
            payments = get_payments_db()
            current_paid = payments.get(selected_student, 0)
            new_paid = current_paid + pay_amount
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO payments (student_name, paid_amount) VALUES (?, ?)
                ON CONFLICT(student_name) DO UPDATE SET paid_amount = ?
            ''', (selected_student, new_paid, new_paid))
            conn.commit()
            conn.close()
            
            st.success(f"Successfully collected {pay_amount} Taka from {selected_student}!")
            st.rerun()
        else:
            st.warning("Please enter a valid amount greater than 0.")

# ----------------- 5. MANAGE MEMBERS VIEW -----------------
elif nav_mode == "Manage Members":
    st.markdown("### 👥 Manage Members")
    st.write("নতুন শিক্ষার্থী যোগ করুন অথবা প্রাইভেট ছেড়ে যাওয়া শিক্ষার্থীকে তালিকা থেকে বাদ দিন।")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Add New Student")
        new_name = st.text_input("Student Name")
        if st.button("Add Student"):
            if new_name and new_name not in students:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO students (name) VALUES (?)", (new_name,))
                conn.commit()
                conn.close()
                st.success(f"Successfully added {new_name}!")
                st.rerun()
            elif new_name in students:
                st.warning("Student already exists!")
            else:
                st.warning("Please enter a valid name.")

    with col2:
        st.markdown("#### Remove Student")
        rem_student = st.selectbox("Select Student to Remove", students)
        if st.button("Remove Student"):
            if rem_student in students:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM students WHERE name = ?", (rem_student,))
                cursor.execute("DELETE FROM attendance WHERE student_name = ?", (rem_student,))
                cursor.execute("DELETE FROM payments WHERE student_name = ?", (rem_student,))
                cursor.execute("DELETE FROM initial_fines WHERE student_name = ?", (rem_student,))
                conn.commit()
                conn.close()
                st.success(f"Successfully removed {rem_student}!")
                st.rerun()

    st.markdown("---")
    st.markdown("#### Current Student List")
    st.write(", ".join(students))

# ----------------- 6. FINE SETTING VIEW -----------------
elif nav_mode == "Fine Setting":
    st.markdown("### ⚙️ Fine Settings")
    st.write("সাধারণ দিনের ফাইন রেট এবং পরীক্ষার দিন বা বিশেষ দিনের জন্য আলাদা ফাইন সেট করুন।")

    fine_settings = get_fine_settings_db()
    current_regular = fine_settings.get("regular", 20)
    special_dates = fine_settings.get("special_dates", {})
    
    new_regular = st.number_input("Regular Fine Amount (Per Absent)", min_value=0, value=int(current_regular), step=5)
    
    st.markdown("#### Special / Exam Day Fine")
    st.write("যেদিন পরীক্ষা বা বিশেষ দিন থাকবে, সেই তারিখের জন্য আলাদা ফাইন পরিমাণ নির্ধারণ করুন।")
    
    selected_spec_date = st.date_input("Select Special Date", datetime.strptime(today_str(), "%Y-%m-%d"))
    spec_date_str = selected_spec_date.strftime("%Y-%m-%d")
    
    existing_spec_fine = special_dates.get(spec_date_str, 30)
    new_spec_fine = st.number_input(f"Fine for {format_date(spec_date_str)} (Taka)", min_value=0, value=int(existing_spec_fine), step=5)

    if st.button("Save Fine Settings"):
        special_dates[spec_date_str] = new_spec_fine
        save_fine_settings_db(new_regular, special_dates)
        st.success("Fine settings updated successfully!")
        st.rerun()

# ----------------- 7. RESET VIEW -----------------
elif nav_mode == "Reset":
    st.markdown("### ⚠️ Reset All Data")
    st.warning("সতর্কতা: রিসেট করলে সমস্ত শিক্ষার্থীর উপস্থিতি, হিস্ট্রি এবং ফাইন/বকেয়ার হিসাব মুছে গিয়ে অ্যাপটি একদম নতুন অবস্থায় চলে যাবে।")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Cancel"):
            st.rerun()
            
    with col2:
        if st.button("Reset"):
            if os.path.exists(DB_FILE):
                os.remove(DB_FILE)
            init_db()
            st.success("অ্যাপটি সফলভাবে রিসেট করা হয়েছে!")
            st.rerun()
