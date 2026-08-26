import os
import json
from datetime import datetime
import streamlit as st

STUDENTS = [
    "Rounak", "Nirob", "Jahidul", "Abir", "Tafin",
    "Anik", "Muhin", "Mehedi", "Alif", "Samia",
    "Sorna", "Tuli", "Tabassum", "Sumaiya", "Bonna",
    "Runa", "Maria"
]

FINE_PER_ABSENT = 20
INITIAL_FINE = {"Tabassum": 20, "Runa": 20}
DATA_FILE = "attendance_data.json"

st.set_page_config(page_title="Attendance E-Khata", page_icon="📚", layout="centered")

# Custom CSS for UI styling matching your exact requirements
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #24292e; }
    
    /* Bigger and lower title styling (Purple requirement) */
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

    /* Compact Summary Cards */
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

    /* Student Row Wrapper */
    .student-card-box {
        background-color: #f6f8fa;
        border: 1px solid #d0d7de;
        border-radius: 8px;
        padding: 8px 10px;
        margin-bottom: 4px;
    }

    /* Status Badges */
    .badge-present { background-color: #dafbe1; color: #1a7f37; border: 1px solid #2ea043; padding: 3px 8px; border-radius: 5px; font-weight: bold; font-size: 11px; }
    .badge-leave { background-color: #fff8c5; color: #9a6700; border: 1px solid #fb8532; padding: 3px 8px; border-radius: 5px; font-weight: bold; font-size: 11px; }
    .badge-absent { background-color: #ffebe9; color: #cf222e; border: 1px solid #cf222e; padding: 3px 8px; border-radius: 5px; font-weight: bold; font-size: 11px; }
    .badge-none { background-color: #eaeef2; color: #57606a; padding: 3px 8px; border-radius: 5px; font-size: 11px; }

    /* Custom Red Buttons with Equal size and Yellow Text */
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
    .stButton button:hover {
        background-color: #b51f2b !important;
        color: #fff !important;
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

def blank_day():
    return {name: "" for name in STUDENTS}

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"days": {}, "initial_fine": INITIAL_FINE.copy(), "payments": {}}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("days", {})
        data.setdefault("initial_fine", INITIAL_FINE.copy())
        data.setdefault("payments", {})
        for day in data["days"].values():
            for name in STUDENTS:
                day.setdefault(name, "")
        return data
    except:
        return {"days": {}, "initial_fine": INITIAL_FINE.copy(), "payments": {}}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data

# Sidebar Menu with Top-Right Hamburger Look & Feel
with st.sidebar:
    st.markdown("### ☰ Navigation Menu")
    nav_mode = st.radio(
        "Menu", ["Dashboard", "History", "Total Fine", "Collect Fee"], label_visibility="collapsed"
    )

# App Header (Bigger and Lower as requested)
st.markdown('<div class="app-header">📚 Attendance E-Khata</div>', unsafe_allow_html=True)

# Date Selection
selected_date_obj = st.date_input(
    "Select Date", datetime.strptime(today_str(), "%Y-%m-%d")
)
current_date = selected_date_obj.strftime("%Y-%m-%d")

if current_date not in data["days"]:
    data["days"][current_date] = blank_day()
    data["days"][current_date]["Nirob"] = "LEAVE"
    save_data(data)

def get_current_fines():
    fines = {s: int(data["initial_fine"].get(s, 0)) for s in STUDENTS}
    for d_item in data["days"].values():
        for student, status in d_item.items():
            if status == "ABSENT":
                fines[student] = fines.get(student, 0) + FINE_PER_ABSENT
    
    payments = data.get("payments", {})
    net_fines = {}
    for s in STUDENTS:
        total_due = fines.get(s, 0)
        paid = payments.get(s, 0)
        net_fines[s] = max(0, total_due - paid)
    return net_fines

# ----------------- 1. DASHBOARD VIEW -----------------
if nav_mode == "Dashboard":
    day_data = data["days"].setdefault(current_date, blank_day())

    present = sum(day_data.get(s) == "PRESENT" for s in STUDENTS)
    leave = sum(day_data.get(s) == "LEAVE" for s in STUDENTS)
    absent = sum(day_data.get(s) == "ABSENT" for s in STUDENTS)
    not_set = len(STUDENTS) - present - leave - absent

    net_fines = get_current_fines()
    total_fine_amount = sum(net_fines.values())

    # Summary Cards
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

    # Render each student row with equal red buttons & yellow text
    for student in STUDENTS:
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
            
            # Equal sized action buttons with yellow text
            b_cols = st.columns(3)
            if b_cols[0].button("✔️ PRESENT", key=f"btn_p_{student}"):
                data["days"][current_date][student] = "PRESENT"
                save_data(data)
                st.rerun()
            if b_cols[1].button("👤 LEAVE", key=f"btn_l_{student}"):
                data["days"][current_date][student] = "LEAVE"
                save_data(data)
                st.rerun()
            if b_cols[2].button("❌ ABSENT", key=f"btn_a_{student}"):
                data["days"][current_date][student] = "ABSENT"
                save_data(data)
                st.rerun()
            st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

# ----------------- 2. HISTORY VIEW -----------------
elif nav_mode == "History":
    st.subheader("📅 Attendance History")
    sorted_dates = sorted(data["days"].keys(), reverse=True)

    if not sorted_dates:
        st.info("No attendance history found yet.")
    else:
        for d in sorted_dates:
            day = data["days"][d]
            p = sum(day.get(s) == "PRESENT" for s in STUDENTS)
            l = sum(day.get(s) == "LEAVE" for s in STUDENTS)
            a = sum(day.get(s) == "ABSENT" for s in STUDENTS)

            with st.expander(f"{format_date(d)}  —  Present: {p} | Leave: {l} | Absent: {a}"):
                history_list = [{"Student": s, "Status": day.get(s, "-") or "-"} for s in STUDENTS]
                st.table(history_list)

# ----------------- 3. TOTAL FINE VIEW -----------------
elif nav_mode == "Total Fine":
    st.subheader("💰 Total Due / Fine List")
    net_fines = get_current_fines()
    payments = data.get("payments", {})

    fine_data = [
        {
            "Student Name": s, 
            "Paid": f"{payments.get(s, 0)} Tk", 
            "Remaining Due": f"{net_fines.get(s, 0)} Tk"
        }
        for s in STUDENTS
    ]
    st.table(fine_data)

# ----------------- 4. COLLECT FEE VIEW -----------------
elif nav_mode == "Collect Fee":
    st.subheader("💵 Collect Fine / Clear Dues")
    st.write("বকেয়া টাকা পরিশোধ করলে এখানে এন্ট্রি দিন, যা মোট বকেয়া থেকে স্বয়ংক্রিয়ভাবে মাইনাস হয়ে যাবে।")

    net_fines = get_current_fines()
    selected_student = st.selectbox("Select Student", STUDENTS)
    current_due = net_fines.get(selected_student, 0)
    
    st.info(f"Current Due for {selected_student}: **{current_due} Taka**")
    pay_amount = st.number_input("Enter Amount to Pay (Taka)", min_value=0, step=10)

    if st.button("Confirm Payment"):
        if pay_amount > 0:
            current_paid = data.setdefault("payments", {}).get(selected_student, 0)
            data["payments"][selected_student] = current_paid + pay_amount
            save_data(data)
            st.success(f"Successfully collected {pay_amount} Taka from {selected_student}!")
            st.rerun()
        else:
            st.warning("Please enter a valid amount greater than 0.")
