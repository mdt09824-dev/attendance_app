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

# Custom CSS for UI adjustments matching your requirements
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Reduce top spacing */
    .block-container { padding-top: 1rem !important; }

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
        min-height: 55px;
    }
    .c-present { background-color: #1b3b22; border: 1px solid #28a745; }
    .c-leave { background-color: #3b331b; border: 1px solid #ffc107; }
    .c-absent { background-color: #3b1b1b; border: 1px solid #dc3545; }
    .c-fee { background-color: #1b283b; border: 1px solid #007bff; }

    .stat-card small { font-size: 10px; color: #d0d7de; }
    .stat-card h4 { font-size: 14px; margin: 0; font-weight: bold; }

    /* Student table badges */
    .badge-p { color: #3fb950; font-weight: bold; font-size: 12px; }
    .badge-l { color: #d29922; font-weight: bold; font-size: 12px; }
    .badge-a { color: #f85149; font-weight: bold; font-size: 12px; }
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

# Sidebar Menu (Hamburger Icon Style)
with st.sidebar:
    st.markdown("### ☰ Menu")
    nav_mode = st.radio(
        "Navigation", ["Dashboard", "History", "Total Fine", "Collect Fee"], label_visibility="collapsed"
    )

# App Header (Moved up closer)
st.markdown("### 📚 Attendance E-Khata")
st.markdown("---")

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

    # Compact Summary Cards with smaller text values
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

    # Student list rows
    for student in STUDENTS:
        current_status = day_data.get(student, "")
        status_display = "-"
        if current_status == "PRESENT":
            status_display = '<span class="badge-p">PRESENT</span>'
        elif current_status == "LEAVE":
            status_display = '<span class="badge-l">LEAVE</span>'
        elif current_status == "ABSENT":
            status_display = '<span class="badge-a">ABSENT</span>'

        cols = st.columns([2.2, 2.3, 3.5])
        cols[0].markdown(f"**{student}**", unsafe_allow_html=True)
        cols[1].markdown(status_display, unsafe_allow_html=True)
        
        b_cols = cols[2].columns(3)
        if b_cols[0].button("P", key=f"btn_p_{student}"):
            data["days"][current_date][student] = "PRESENT"
            save_data(data)
            st.rerun()
        if b_cols[1].button("L", key=f"btn_l_{student}"):
            data["days"][current_date][student] = "LEAVE"
            save_data(data)
            st.rerun()
        if b_cols[2].button("A", key=f"btn_a_{student}"):
            data["days"][current_date][student] = "ABSENT"
            save_data(data)
            st.rerun()

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
