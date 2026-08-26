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

INITIAL_FINE = {
    "Tabassum": 20,
    "Runa": 20
}

DATA_FILE = "attendance_data.json"

# Page Configuration
st.set_page_config(
    page_title="Private Attendance E-Khata",
    page_icon="📚",
    layout="centered"
)


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
        return {
            "days": {},
            "initial_fine": INITIAL_FINE.copy(),
            "payments": {}  # Track paid amounts per student
        }
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
        return {
            "days": {},
            "initial_fine": INITIAL_FINE.copy(),
            "payments": {}
        }


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# Load data into session state
if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data

# Custom CSS for styling to match the modern look
st.markdown("""
    <style>
    .metric-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# App Header
st.title("📚 Attendance E-Khata")

# Navigation selection via Radio or selectbox mimicking bottom/sidebar tabs
nav_mode = st.radio(
    "Navigation", ["Dashboard", "History", "Total Fine", "Collect Fee"], horizontal=True
)
st.divider()

# Date Selection for Attendance
selected_date_obj = st.date_input(
    "Select Date", datetime.strptime(today_str(), "%Y-%m-%d")
)
current_date = selected_date_obj.strftime("%Y-%m-%d")

if current_date not in data["days"]:
    data["days"][current_date] = blank_day()
    data["days"][current_date]["Nirob"] = "LEAVE"
    save_data(data)

# Helper function to calculate current fines minus payments
def get_current_fines():
    fines = {s: int(data["initial_fine"].get(s, 0)) for s in STUDENTS}
    for d_item in data["days"].values():
        for student, status in d_item.items():
            if status == "ABSENT":
                fines[student] = fines.get(student, 0) + FINE_PER_ABSENT
    
    # Subtract paid amounts
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

    # Summary calculation
    present = sum(day_data.get(s) == "PRESENT" for s in STUDENTS)
    leave = sum(day_data.get(s) == "LEAVE" for s in STUDENTS)
    absent = sum(day_data.get(s) == "ABSENT" for s in STUDENTS)
    not_set = len(STUDENTS) - present - leave - absent

    net_fines = get_current_fines()
    total_fine_amount = sum(net_fines.values())

    # Top Metric Summary Cards layout
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Present", f"{present}", "Students")
    col2.metric("Leave", f"{leave}", "Students")
    col3.metric("Absent", f"{absent}", "Students")
    col4.metric("Total Due", f"{total_fine_amount} Tk")

    st.divider()

    # Table Header
    c1, c2, c3 = st.columns([2, 2, 3])
    c1.markdown("**Name**")
    c2.markdown("**Status**")
    c3.markdown("**Action (P / L / A)**")

    # Student Rows with Action Buttons
    for student in STUDENTS:
        col_name, col_status, col_action = st.columns([2, 2, 3])

        col_name.write(student)
        current_status = day_data.get(student, "")
        
        if current_status == "PRESENT":
            col_status.success("PRESENT")
        elif current_status == "LEAVE":
            col_status.warning("LEAVE")
        elif current_status == "ABSENT":
            col_status.error("ABSENT")
        else:
            col_status.write("-")

        # Action Buttons inside columns
        b1, b2, b3 = col_action.columns(3)
        if b1.button("P", key=f"p_{student}"):
            data["days"][current_date][student] = "PRESENT"
            save_data(data)
            st.rerun()

        if b2.button("L", key=f"l_{student}"):
            data["days"][current_date][student] = "LEAVE"
            save_data(data)
            st.rerun()

        if b3.button("A", key=f"a_{student}"):
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

# ----------------- 4. COLLECT FEE VIEW (New Option) -----------------
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
