import os
import json
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

DATA_FILE = "attendance_data.json"

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

def blank_day(students):
    return {name: "" for name in students}

def load_data():
    if not os.path.exists(DATA_FILE):
        return {
            "students": DEFAULT_STUDENTS.copy(),
            "days": {},
            "initial_fine": INITIAL_FINE.copy(),
            "payments": {},
            "fine_settings": {
                "regular": 20,
                "special_dates": {} # format: {"YYYY-MM-DD": 30}
            }
        }
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("students", DEFAULT_STUDENTS.copy())
        data.setdefault("days", {})
        data.setdefault("initial_fine", INITIAL_FINE.copy())
        data.setdefault("payments", {})
        data.setdefault("fine_settings", {"regular": 20, "special_dates": {}})
        
        students = data["students"]
        for day in data["days"].values():
            for name in students:
                day.setdefault(name, "")
        return data
    except:
        return {
            "students": DEFAULT_STUDENTS.copy(),
            "days": {},
            "initial_fine": INITIAL_FINE.copy(),
            "payments": {},
            "fine_settings": {"regular": 20, "special_dates": {}}
        }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data
students = data["students"]

# Sidebar Navigation Menu with exact requested order (Reset at the bottom)
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

if current_date not in data["days"]:
    data["days"][current_date] = blank_day(students)
    save_data(data)

def get_current_fines():
    fine_settings = data.get("fine_settings", {"regular": 20, "special_dates": {}})
    regular_fine = fine_settings.get("regular", 20)
    special_dates = fine_settings.get("special_dates", {})

    fines = {s: int(data["initial_fine"].get(s, 0)) for s in students}
    
    for d_str, d_item in data["days"].items():
        current_day_fine = special_dates.get(d_str, regular_fine)
        for student, status in d_item.items():
            if status == "ABSENT":
                if student in fines:
                    fines[student] = fines.get(student, 0) + current_day_fine
    
    payments = data.get("payments", {})
    net_fines = {}
    for s in students:
        total_due = fines.get(s, 0)
        paid = payments.get(s, 0)
        net_fines[s] = max(0, total_due - paid)
    return net_fines, fines

# ----------------- 1. DASHBOARD VIEW -----------------
if nav_mode == "Dashboard":
    day_data = data["days"].setdefault(current_date, blank_day(students))

    present = sum(day_data.get(s) == "PRESENT" for s in students)
    leave = sum(day_data.get(s) == "LEAVE" for s in students)
    absent = sum(day_data.get(s) == "ABSENT" for s in students)
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
    st.markdown("### 📅 Attendance History")
    sorted_dates = sorted(data["days"].keys(), reverse=True)

    if not sorted_dates:
        st.info("No attendance history found yet.")
    else:
        for d in sorted_dates:
            day = data["days"][d]
            p = sum(day.get(s) == "PRESENT" for s in students)
            l = sum(day.get(s) == "LEAVE" for s in students)
            a = sum(day.get(s) == "ABSENT" for s in students)

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
    payments = data.get("payments", {})

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
            current_paid = data.setdefault("payments", {}).get(selected_student, 0)
            data["payments"][selected_student] = current_paid + pay_amount
            save_data(data)
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
                students.append(new_name)
                data["students"] = students
                for d in data["days"].values():
                    d[new_name] = ""
                save_data(data)
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
                students.remove(rem_student)
                data["students"] = students
                for d in data["days"].values():
                    d.pop(rem_student, None)
                save_data(data)
                st.success(f"Successfully removed {rem_student}!")
                st.rerun()

    st.markdown("---")
    st.markdown("#### Current Student List")
    st.write(", ".join(students))

# ----------------- 6. FINE SETTING VIEW -----------------
elif nav_mode == "Fine Setting":
    st.markdown("### ⚙️ Fine Settings")
    st.write("সাধারণ দিনের ফাইন রেট এবং পরীক্ষার দিন বা বিশেষ দিনের জন্য আলাদা ফাইন সেট করুন।")

    fine_settings = data.setdefault("fine_settings", {"regular": 20, "special_dates": {}})
    
    current_regular = fine_settings.get("regular", 20)
    new_regular = st.number_input("Regular Fine Amount (Per Absent)", min_value=0, value=int(current_regular), step=5)
    
    st.markdown("#### Special / Exam Day Fine")
    st.write("যেদিন পরীক্ষা বা বিশেষ দিন থাকবে, সেই তারিখের জন্য আলাদা ফাইন পরিমাণ নির্ধারণ করুন।")
    
    selected_spec_date = st.date_input("Select Special Date", datetime.strptime(today_str(), "%Y-%m-%d"))
    spec_date_str = selected_spec_date.strftime("%Y-%m-%d")
    
    existing_spec_fine = fine_settings["special_dates"].get(spec_date_str, 30)
    new_spec_fine = st.number_input(f"Fine for {format_date(spec_date_str)} (Taka)", min_value=0, value=int(existing_spec_fine), step=5)

    if st.button("Save Fine Settings"):
        fine_settings["regular"] = new_regular
        fine_settings["special_dates"][spec_date_str] = new_spec_fine
        data["fine_settings"] = fine_settings
        save_data(data)
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
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
            st.session_state.data = {
                "students": DEFAULT_STUDENTS.copy(),
                "days": {},
                "initial_fine": INITIAL_FINE.copy(),
                "payments": {},
                "fine_settings": {"regular": 20, "special_dates": {}}
            }
            save_data(st.session_state.data)
            st.success("অ্যাপটি সফলভাবে রিসেট করা হয়েছে!")
            st.rerun()
