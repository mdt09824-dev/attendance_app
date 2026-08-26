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
            "initial_fine": INITIAL_FINE.copy()
        }
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("days", {})
        data.setdefault("initial_fine", INITIAL_FINE.copy())
        for day in data["days"].values():
            for name in STUDENTS:
                day.setdefault(name, "")
        return data
    except:
        return {
            "days": {},
            "initial_fine": INITIAL_FINE.copy()
        }


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# Load data into session state
if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data

# App Header
st.title("📚 Private Attendance E-Khata")

# Sidebar for Navigation & Date Selection
st.sidebar.header("Navigation & Date")

selected_date_obj = st.sidebar.date_input(
    "Select Date", datetime.strptime(today_str(), "%Y-%m-%d")
)
current_date = selected_date_obj.strftime("%Y-%m-%d")

if current_date not in data["days"]:
    data["days"][current_date] = blank_day()
    data["days"][current_date]["Nirob"] = "LEAVE"
    save_data(data)

# Sidebar view options
view_mode = st.sidebar.radio(
    "Views", ["Daily Attendance", "Total Fine", "History"]
)

# ----------------- 1. DAILY ATTENDANCE VIEW -----------------
if view_mode == "Daily Attendance":
    st.subheader(f"Date: {format_date(current_date)}")

    day_data = data["days"].setdefault(current_date, blank_day())

    # Summary calculation
    present = sum(day_data.get(s) == "PRESENT" for s in STUDENTS)
    leave = sum(day_data.get(s) == "LEAVE" for s in STUDENTS)
    absent = sum(day_data.get(s) == "ABSENT" for s in STUDENTS)
    not_set = len(STUDENTS) - present - leave - absent

    # Calculate current total fines
    fines = {s: int(data["initial_fine"].get(s, 0)) for s in STUDENTS}
    for d_item in data["days"].values():
        for student, status in d_item.items():
            if status == "ABSENT":
                fines[student] = fines.get(student, 0) + 20
    total_fine_amount = sum(fines.values())

    st.metric(
        label="Summary",
        value=f"Present: {present} | Leave: {leave} | Absent: {absent} | Not Set: {not_set}",
        delta=f"Total Fine: {total_fine_amount} Taka",
    )
    st.divider()

    # Table Header
    col1, col2, col3 = st.columns([2, 2, 3])
    col1.markdown("**Name**")
    col2.markdown("**Current Status**")
    col3.markdown("**Action**")

    # Student Rows
    for student in STUDENTS:
        c1, c2, c3 = st.columns([2, 2, 3])

        c1.write(student)
        current_status = day_data.get(student, "")
        c2.write(current_status if current_status else "-")

        # Action Buttons using columns inside c3
# Radio buttons or selectbox can also be used, but buttons feel like app controls
        btn_col1, btn_col2, btn_col3 = c3.columns(3)

        if btn_col1.button("P", key=f"p_{student}"):
            data["days"][current_date][student] = "PRESENT"
            save_data(data)
            st.rerun()

        if btn_col2.button("L", key=f"l_{student}"):
            data["days"][current_date][student] = "LEAVE"
            save_data(data)
            st.rerun()

        if btn_col3.button("A", key=f"a_{student}"):
            data["days"][current_date][student] = "ABSENT"
            save_data(data)
            st.rerun()

# ----------------- 2. TOTAL FINE VIEW -----------------
elif view_mode == "Total Fine":
    st.subheader("💰 Total Fine List")

    fines = {s: int(data["initial_fine"].get(s, 0)) for s in STUDENTS}
    for d_item in data["days"].values():
        for student, status in d_item.items():
            if status == "ABSENT":
                fines[student] = fines.get(student, 0) + 20

    # Display in a clean table format
    fine_data = [
        {"Student Name": s, "Total Fine": f"{fines.get(s, 0)} Taka"}
        for s in STUDENTS
    ]
    st.table(fine_data)

# ----------------- 3. HISTORY VIEW -----------------
elif view_mode == "History":
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

            with st.expander(
                f"{format_date(d)}  —  Present: {p} | Leave: {l} | Absent: {a}"
            ):
                # Show details of that specific day
                history_list = [
                    {"Student": s, "Status": day.get(s, "-") or "-"}
                    for s in STUDENTS
                ]
                st.table(history_list)
