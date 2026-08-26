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

# Advanced Custom CSS to style everything like a sleek mobile app UI
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .card-container {
        display: flex;
        gap: 8px;
        margin-bottom: 15px;
    }
    .stat-card {
        flex: 1;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        color: white;
    }
    .c-present { background-color: #1b3b22; border: 1px solid #28a745; }
    .c-leave { background-color: #3b331b; border: 1px solid #ffc107; }
    .c-absent { background-color: #3b1b1b; border: 1px solid #dc3545; }
    .c-fee { background-color: #1b283b; border: 1px solid #007bff; }

    /* Custom Table Layout for Students */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
        background-color: #161b22;
        border-radius: 8px;
        overflow: hidden;
    }
    .styled-table th, .styled-table td {
        padding: 10px 8px;
        text-align: left;
        border-bottom: 1px solid #30363d;
        font-size: 14px;
    }
    .styled-table th {
        background-color: #21262d;
        color: #8b949e;
    }
    .badge-p { color: #3fb950; font-weight: bold; }
    .badge-l { color: #d29922; font-weight: bold; }
    .badge-a { color: #f85149; font-weight: bold; }
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

# Query parameters for updating attendance via buttons seamlessly
query_params = st.query_params
if "action" in query_params and "student" in query_params and "date" in query_params:
    act = query_params["action"]
    stud = query_params["student"]
    dt = query_params["date"]
    if dt in data["days"] and stud in STUDENTS:
        if act == "P":
            data["days"][dt][stud] = "PRESENT"
        elif act == "L":
            data["days"][dt][stud] = "LEAVE"
        elif act == "A":
            data["days"][dt][stud] = "ABSENT"
        save_data(data)
        st.query_params.clear()
        st.rerun()

st.markdown("### 📚 Attendance E-Khata")

# Navigation Tabs
nav_mode = st.radio(
    "Menu", ["Dashboard", "History", "Total Fine", "Collect Fee"], horizontal=True
)
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

    # Summary Cards Layout
    st.markdown(f"""
        <div class="card-container">
            <div class="stat-card c-present">
                <small>Present</small>
                <h3>{present}</h3>
            </div>
            <div class="stat-card c-leave">
                <small>Leave</small>
                <h3>{leave}</h3>
            </div>
            <div class="stat-card c-absent">
                <small>Absent</small>
                <h3>{absent}</h3>
            </div>
            <div class="stat-card c-fee">
                <small>Total Due</small>
                <h3>{total_fine_amount}Tk</h3>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(f"**Date:** {format_date(current_date)} &nbsp;|&nbsp; **Not Set:** {not_set}")
    st.markdown("---")

    # Render clean inline table with Streamlit buttons for each row
    for student in STUDENTS:
        current_status = day_data.get(student, "")
        status_display = "-"
        if current_status == "PRESENT":
            status_display = '<span class="badge-p">PRESENT</span>'
        elif current_status == "LEAVE":
            status_display = '<span class="badge-l">LEAVE</span>'
        elif current_status == "ABSENT":
            status_display = '<span class="badge-a">ABSENT</span>'

        cols = st.columns([2.5, 2.5, 3])
        cols[0].markdown(f"**{student}**", unsafe_allow_html=True)
        cols[1].markdown(status_display, unsafe_allow_html=True)
        
        # Action buttons packed neatly in columns
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
