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

st.set_page_config(
    page_title="Attendance E-Khata",
    page_icon="📚",
    layout="centered"
)

# ================= CUSTOM CSS =================
st.markdown("""
<style>

.stApp {
    background-color: #ffffff;
    color: #24292e;
}

.block-container {
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
}

/* Summary Cards */
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

.c-present {
    background-color: #2ea043;
}

.c-leave {
    background-color: #fb8532;
}

.c-absent {
    background-color: #cf222e;
}

.c-fee {
    background-color: #0969da;
}

.stat-card small {
    font-size: 10px;
    color: white;
}

.stat-card h4 {
    font-size: 13px;
    margin: 0;
    font-weight: bold;
    color: white;
}

/* Student Row */
.student-box {
    background-color: #f6f8fa;
    border: 1px solid #d0d7de;
    border-radius: 8px;
    padding: 7px 6px;
    margin-bottom: 6px;
}

/* Student Name */
.student-name {
    font-size: 14px;
    font-weight: 700;
    color: #24292e;
    white-space: nowrap;
}

/* Status */
.status-badge {
    display: inline-block;
    font-size: 10px;
    padding: 4px 6px;
    border-radius: 5px;
    font-weight: bold;
    text-align: center;
    min-width: 65px;
}

.badge-present {
    background-color: #dafbe1;
    color: #1a7f37;
    border: 1px solid #2ea043;
}

.badge-leave {
    background-color: #fff8c5;
    color: #9a6700;
    border: 1px solid #fb8532;
}

.badge-absent {
    background-color: #ffebe9;
    color: #cf2222;
    border: 1px solid #cf2222;
}

.badge-none {
    background-color: #eaeef2;
    color: #57606a;
    border: 1px solid #d0d7de;
}

/* Make Streamlit buttons compact */
div.stButton > button {
    min-height: 34px;
    padding: 2px 5px;
    font-size: 12px;
    border-radius: 6px;
}

/* Mobile adjustment */
@media (max-width: 600px) {

    .student-name {
        font-size: 12px;
    }

    .status-badge {
        font-size: 9px;
        min-width: 52px;
        padding: 3px 4px;
    }

    div.stButton > button {
        font-size: 11px;
        padding: 1px 3px;
    }
}

</style>
""", unsafe_allow_html=True)


# ================= FUNCTIONS =================

def today_str():
    return datetime.now().strftime("%Y-%m-%d")


def format_date(d):
    try:
        return datetime.strptime(
            d, "%Y-%m-%d"
        ).strftime("%d-%m-%Y")
    except:
        return d


def blank_day():
    return {name: "" for name in STUDENTS}


def load_data():

    if not os.path.exists(DATA_FILE):
        return {
            "days": {},
            "initial_fine": INITIAL_FINE.copy(),
            "payments": {}
        }

    try:

        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        data.setdefault("days", {})
        data.setdefault(
            "initial_fine",
            INITIAL_FINE.copy()
        )
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

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


# ================= LOAD DATA =================

if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data


# ================= SIDEBAR =================

with st.sidebar:

    st.markdown("### ☰ Menu")

    nav_mode = st.radio(
        "Navigation",
        [
            "Dashboard",
            "History",
            "Total Fine",
            "Collect Fee"
        ],
        label_visibility="collapsed"
    )


# ================= HEADER =================

st.markdown("### 📚 Attendance E-Khata")

st.markdown("---")


# ================= DATE =================

selected_date_obj = st.date_input(
    "Select Date",
    datetime.strptime(
        today_str(),
        "%Y-%m-%d"
    )
)

current_date = selected_date_obj.strftime(
    "%Y-%m-%d"
)


# Create today's record
if current_date not in data["days"]:

    data["days"][current_date] = blank_day()

    # Default Nirob = Leave
    data["days"][current_date]["Nirob"] = "LEAVE"

    save_data(data)


# ================= FINE CALCULATION =================

def get_current_fines():

    fines = {
        s: int(
            data["initial_fine"].get(s, 0)
        )
        for s in STUDENTS
    }

    for d_item in data["days"].values():

        for student, status in d_item.items():

            if status == "ABSENT":

                fines[student] = (
                    fines.get(student, 0)
                    + FINE_PER_ABSENT
                )

    payments = data.get("payments", {})

    net_fines = {}

    for s in STUDENTS:

        total_due = fines.get(s, 0)

        paid = payments.get(s, 0)

        net_fines[s] = max(
            0,
            total_due - paid
        )

    return net_fines


# =====================================================
#                    DASHBOARD
# =====================================================

if nav_mode == "Dashboard":

    day_data = data["days"].setdefault(
        current_date,
        blank_day()
    )

    present = sum(
        day_data.get(s) == "PRESENT"
        for s in STUDENTS
    )

    leave = sum(
        day_data.get(s) == "LEAVE"
        for s in STUDENTS
    )

    absent = sum(
        day_data.get(s) == "ABSENT"
        for s in STUDENTS
    )

    not_set = (
        len(STUDENTS)
        - present
        - leave
        - absent
    )

    net_fines = get_current_fines()

    total_fine_amount = sum(
        net_fines.values()
    )


    # ================= SUMMARY =================

    st.markdown(
        f"""
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
        """,
        unsafe_allow_html=True
    )


    st.markdown(
        f"**Date:** {format_date(current_date)} "
        f"&nbsp; | &nbsp; "
        f"**Not Set:** {not_set}"
    )

    st.markdown("---")


    # =================================================
    # STUDENT LIST
    # =================================================

    for student in STUDENTS:

        current_status = day_data.get(
            student,
            ""
        )


        # Status design
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


        # =================================================
        # IMPORTANT:
        # Name + Status + Action SAME ROW
        # =================================================

        col_name, col_status, col_p, col_l, col_a = st.columns(
            [3.0, 2.0, 1.7, 1.7, 1.7],
            gap="small"
        )


        # Name
        with col_name:

            st.markdown(
                f"""
                <div class="student-box">
                    <span class="student-name">
                        👤 {student}
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )


        # Status
        with col_status:

            st.markdown(
                f"""
                <div style="
                    padding-top:8px;
                    text-align:center;
                ">
                    <span class="status-badge {status_cls}">
                        {status_text}
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )


        # Present button
        with col_p:

            if st.button(
                "✔ P",
                key=f"btn_p_{student}",
                use_container_width=True
            ):

                data["days"][
                    current_date
                ][student] = "PRESENT"

                save_data(data)

                st.rerun()


        # Leave button
        with col_l:

            if st.button(
                "👤 L",
                key=f"btn_l_{student}",
                use_container_width=True
            ):

                data["days"][
                    current_date
                ][student] = "LEAVE"

                save_data(data)

                st.rerun()


        # Absent button
        with col_a:

            if st.button(
                "❌ A",
                key=f"btn_a_{student}",
                use_container_width=True
            ):

                data["days"][
                    current_date
                ][student] = "ABSENT"

                save_data(data)

                st.rerun()


# =====================================================
#                    HISTORY
# =====================================================

elif nav_mode == "History":

    st.subheader("📅 Attendance History")

    sorted_dates = sorted(
        data["days"].keys(),
        reverse=True
    )

    if not sorted_dates:

        st.info(
            "No attendance history found yet."
        )

    else:

        for d in sorted_dates:

            day = data["days"][d]

            p = sum(
                day.get(s) == "PRESENT"
                for s in STUDENTS
            )

            l = sum(
                day.get(s) == "LEAVE"
                for s in STUDENTS
            )

            a = sum(
                day.get(s) == "ABSENT"
                for s in STUDENTS
            )

            with st.expander(
                f"{format_date(d)}  —  "
                f"Present: {p} | "
                f"Leave: {l} | "
                f"Absent: {a}"
            ):

                history_list = [
                    {
                        "Student": s,
                        "Status": day.get(
                            s,
                            "-"
                        ) or "-"
                    }
                    for s in STUDENTS
                ]

                st.table(history_list)


# =====================================================
#                    TOTAL FINE
# =====================================================

elif nav_mode == "Total Fine":

    st.subheader(
        "💰 Total Due / Fine List"
    )

    net_fines = get_current_fines()

    payments = data.get(
        "payments",
        {}
    )

    fine_data = [

        {
            "Student Name": s,

            "Paid": f"{payments.get(s, 0)} Tk",

            "Remaining Due":
                f"{net_fines.get(s, 0)} Tk"
        }

        for s in STUDENTS

    ]

    st.table(fine_data)


# =====================================================
#                    COLLECT FEE
# =====================================================

elif nav_mode == "Collect Fee":

    st.subheader(
        "💵 Collect Fine / Clear Dues"
    )

    st.write(
        "বকেয়া টাকা পরিশোধ করলে এখানে "
        "এন্ট্রি দিন, যা মোট বকেয়া থেকে "
        "স্বয়ংক্রিয়ভাবে মাইনাস হয়ে যাবে।"
    )

    net_fines = get_current_fines()

    selected_student = st.selectbox(
        "Select Student",
        STUDENTS
    )

    current_due = net_fines.get(
        selected_student,
        0
    )

    st.info(
        f"Current Due for "
        f"{selected_student}: "
        f"**{current_due} Taka**"
    )

    pay_amount = st.number_input(
        "Enter Amount to Pay (Taka)",
        min_value=0,
        step=10
    )

    if st.button(
        "Confirm Payment",
        use_container_width=True
    ):

        if pay_amount > 0:

            current_paid = (
                data
                .setdefault(
                    "payments",
                    {}
                )
                .get(
                    selected_student,
                    0
                )
            )

            data["payments"][
                selected_student
            ] = (
                current_paid
                + pay_amount
            )

            save_data(data)

            st.success(
                f"Successfully collected "
                f"{pay_amount} Taka from "
                f"{selected_student}!"
            )

            st.rerun()

        else:

            st.warning(
                "Please enter a valid "
                "amount greater than 0."
)
