import os
import json
from datetime import datetime, date

import streamlit as st


# =========================================================
# APP CONFIG
# =========================================================

st.set_page_config(
    page_title="Attendance E-Khata",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# =========================================================
# DATA
# =========================================================

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


# =========================================================
# MOBILE CSS
# =========================================================

st.markdown(
    """
    <style>

    /* ---------- PAGE ---------- */

    .stApp {
        background: #f6f8fc;
    }

    .block-container {
        max-width: 480px !important;
        padding-top: 0.5rem !important;
        padding-left: 12px !important;
        padding-right: 12px !important;
        padding-bottom: 90px !important;
    }

    header {
        visibility: hidden;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }


    /* ---------- GLOBAL ---------- */

    * {
        box-sizing: border-box;
    }

    h1, h2, h3, h4, p {
        margin-top: 0 !important;
    }


    /* ---------- TOP HEADER ---------- */

    .top-header {
        margin: -8px -12px 15px -12px;
        padding: 18px 18px;
        border-radius: 0 0 24px 24px;
        background: linear-gradient(
            135deg,
            #087af5,
            #3856e8,
            #7730ed
        );
        color: white;
        box-shadow: 0 8px 20px rgba(59, 79, 225, 0.25);
    }

    .top-title {
        font-size: 23px;
        font-weight: 700;
        margin: 0;
    }

    .top-subtitle {
        font-size: 12px;
        margin-top: 4px;
        opacity: 0.9;
    }


    /* ---------- BUTTONS ---------- */

    .stButton > button {
        width: 100%;
        min-height: 38px;
        border-radius: 10px !important;
        font-weight: 600 !important;
        border: 1px solid #d8deea !important;
        background: white !important;
        color: #2b354d !important;
    }

    .stButton > button:hover {
        border-color: #4773ed !important;
        color: #275fe0 !important;
    }


    /* ---------- DATE INPUT ---------- */

    div[data-baseweb="input"] {
        border-radius: 11px !important;
    }

    div[data-baseweb="select"] {
        border-radius: 11px !important;
    }


    /* ---------- TABS / NAV ---------- */

    div[role="radiogroup"] {
        gap: 6px !important;
    }

    div[role="radiogroup"] label {
        background: white !important;
        border: 1px solid #e0e5ef !important;
        border-radius: 11px !important;
        padding: 8px 10px !important;
    }


    /* ---------- TABLE ---------- */

    .student-name {
        font-size: 14px;
        font-weight: 600;
        color: #273149;
    }

    .small-text {
        font-size: 12px;
        color: #717a8d;
    }


    /* ---------- FOOTER SPACE ---------- */

    .bottom-space {
        height: 65px;
    }


    /* ---------- MOBILE ---------- */

    @media (max-width: 500px) {

        .top-title {
            font-size: 21px;
        }

        .block-container {
            padding-left: 10px !important;
            padding-right: 10px !important;
        }

    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# FUNCTIONS
# =========================================================

def today_str():
    return datetime.now().strftime("%Y-%m-%d")


def format_date(value):
    try:
        return datetime.strptime(
            value,
            "%Y-%m-%d"
        ).strftime("%d-%m-%Y")
    except Exception:
        return value


def blank_day():
    return {
        student: ""
        for student in STUDENTS
    }


def default_data():
    return {
        "days": {},
        "initial_fine": INITIAL_FINE.copy(),
        "payments": {}
    }


def load_data():

    if not os.path.exists(DATA_FILE):
        return default_data()

    try:

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        data.setdefault("days", {})
        data.setdefault(
            "initial_fine",
            INITIAL_FINE.copy()
        )
        data.setdefault(
            "payments",
            {}
        )

        for day in data["days"].values():

            for student in STUDENTS:
                day.setdefault(
                    student,
                    ""
                )

        return data

    except Exception:

        return default_data()


def save_data(data):

    try:

        with open(
            DATA_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2
            )

    except Exception as error:

        st.error(
            f"Data save error: {error}"
        )


def get_total_fines():

    fines = {}

    for student in STUDENTS:

        fines[student] = int(
            data["initial_fine"].get(
                student,
                0
            )
        )

    for day in data["days"].values():

        for student in STUDENTS:

            if day.get(student) == "ABSENT":

                fines[student] += FINE_PER_ABSENT

    return fines


def get_paid_amounts():

    return data.get(
        "payments",
        {}
    )


def get_remaining_fines():

    total_fines = get_total_fines()
    payments = get_paid_amounts()

    remaining = {}

    for student in STUDENTS:

        total = total_fines.get(
            student,
            0
        )

        paid = payments.get(
            student,
            0
        )

        remaining[student] = max(
            0,
            total - paid
        )

    return remaining


# =========================================================
# LOAD DATA
# =========================================================

if "data" not in st.session_state:

    st.session_state.data = load_data()


data = st.session_state.data


# =========================================================
# DEFAULT TODAY
# =========================================================

if today_str() not in data["days"]:

    data["days"][today_str()] = blank_day()

    # Example initial leave
    if "Nirob" in STUDENTS:
        data["days"][today_str()]["Nirob"] = "LEAVE"

    save_data(data)


# =========================================================
# CURRENT PAGE
# =========================================================

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"


# =========================================================
# SELECTED DATE
# =========================================================

if "selected_date" not in st.session_state:

    st.session_state.selected_date = (
        datetime.strptime(
            today_str(),
            "%Y-%m-%d"
        ).date()
    )


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div class="top-header">
        <div class="top-title">
            ☰ &nbsp; Attendance E-Khata
        </div>

        <div class="top-subtitle">
            Attendance & Fee Management
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# TOP NAVIGATION
# =========================================================

nav1, nav2, nav3, nav4 = st.columns(4)

with nav1:

    if st.button(
        "🏠\nDashboard",
        key="dashboard_nav",
        use_container_width=True
    ):
        st.session_state.page = "Dashboard"
        st.rerun()


with nav2:

    if st.button(
        "◷\nHistory",
        key="history_nav",
        use_container_width=True
    ):
        st.session_state.page = "History"
        st.rerun()


with nav3:

    if st.button(
        "💳\nTotal Fine",
        key="fine_nav",
        use_container_width=True
    ):
        st.session_state.page = "Total Fine"
        st.rerun()


with nav4:

    if st.button(
        "•••\nMore",
        key="more_nav",
        use_container_width=True
    ):
        st.session_state.page = "Collect Fee"
        st.rerun()


st.write("")


# =========================================================
# DASHBOARD
# =========================================================

if st.session_state.page == "Dashboard":

    # -----------------------------------------------------
    # DATE
    # -----------------------------------------------------

    selected_date = st.date_input(
        "Select Date",
        value=st.session_state.selected_date,
        key="date_selector"
    )

    if selected_date != st.session_state.selected_date:

        st.session_state.selected_date = selected_date

    current_date = (
        st.session_state.selected_date
        .strftime("%Y-%m-%d")
    )


    # Create day
    if current_date not in data["days"]:

        data["days"][current_date] = blank_day()
        save_data(data)


    day_data = data["days"][current_date]


    # -----------------------------------------------------
    # COUNTS
    # -----------------------------------------------------

    present = sum(
        day_data.get(student) == "PRESENT"
        for student in STUDENTS
    )

    leave = sum(
        day_data.get(student) == "LEAVE"
        for student in STUDENTS
    )

    absent = sum(
        day_data.get(student) == "ABSENT"
        for student in STUDENTS
    )

    not_set = (
        len(STUDENTS)
        - present
        - leave
        - absent
    )


    # -----------------------------------------------------
    # FEE
    # -----------------------------------------------------

    total_fines = get_total_fines()
    remaining_fines = get_remaining_fines()

    total_fee = sum(
        total_fines.values()
    )

    after_payment = sum(
        remaining_fines.values()
    )


    # =====================================================
    # DATE SUMMARY
    # =====================================================

    st.container(border=True)

    st.markdown(
        f"### 📅 {format_date(current_date)}"
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"**🟢 Present**  \n"
            f"### {present}"
        )

    with c2:
        st.markdown(
            f"**🟠 Leave**  \n"
            f"### {leave}"
        )

    with c3:
        st.markdown(
            f"**🔴 Absent**  \n"
            f"### {absent}"
        )

    with c4:
        st.markdown(
            f"**⚪ Not Set**  \n"
            f"### {not_set}"
        )


    st.write("")


    # =====================================================
    # FEE SUMMARY
    # =====================================================

    st.subheader("💰 Fee Summary")

    fee1, fee2 = st.columns(2)

    with fee1:

        st.info(
            f"### {total_fee} Tk\n"
            f"Total Fee"
        )

    with fee2:

        if after_payment > 0:

            st.success(
                f"### {after_payment} Tk\n"
                f"After Payment"
            )

        else:

            st.success(
                "### 0 Tk\n"
                "All Paid"
            )


    # =====================================================
    # PAYMENT BUTTON
    # =====================================================

    if st.button(
        "💳  Collect / Pay Fee",
        key="collect_dashboard",
        use_container_width=True
    ):

        st.session_state.page = "Collect Fee"
        st.rerun()


    # =====================================================
    # STUDENTS
    # =====================================================

    st.subheader("👥 Students")


    for index, student in enumerate(STUDENTS):

        status = day_data.get(
            student,
            ""
        )

        # ---------------------------------------------
        # STATUS TEXT
        # ---------------------------------------------

        if status == "PRESENT":

            status_text = "🟢 PRESENT"

        elif status == "LEAVE":

            status_text = "🟠 LEAVE"

        elif status == "ABSENT":

            status_text = "🔴 ABSENT"

        else:

            status_text = "⚪ NOT SET"


        # ---------------------------------------------
        # STUDENT NAME
        # ---------------------------------------------

        st.markdown(
            f"**{student}**  \n"
            f"<span style='color:#687287;font-size:12px'>"
            f"{status_text}"
            f"</span>",
            unsafe_allow_html=True
        )


        # ---------------------------------------------
        # ACTION BUTTONS
        # ---------------------------------------------

        b1, b2, b3 = st.columns(3)


        with b1:

            if st.button(
                "✓ P",
                key=f"present_{current_date}_{index}",
                use_container_width=True
            ):

                data["days"][
                    current_date
                ][student] = "PRESENT"

                save_data(data)

                st.rerun()


        with b2:

            if st.button(
                "👤 L",
                key=f"leave_{current_date}_{index}",
                use_container_width=True
            ):

                data["days"][
                    current_date
                ][student] = "LEAVE"

                save_data(data)

                st.rerun()


        with b3:

            if st.button(
                "✕ A",
                key=f"absent_{current_date}_{index}",
                use_container_width=True
            ):

                data["days"][
                    current_date
                ][student] = "ABSENT"

                save_data(data)

                st.rerun()


        st.divider()


    # =====================================================
    # TOTAL FINE
    # =====================================================

    st.subheader("💵 Total Fine (Now)")

    if after_payment > 0:

        st.warning(
            f"Current Outstanding: **{after_payment} Tk**"
        )

    else:

        st.success(
            "All outstanding fees are paid."
        )


# =========================================================
# HISTORY
# =========================================================

elif st.session_state.page == "History":

    st.subheader("📅 Attendance History")

    sorted_dates = sorted(
        data["days"].keys(),
        reverse=True
    )

    if not sorted_dates:

        st.info(
            "No attendance history found."
        )

    else:

        for day_date in sorted_dates:

            day = data["days"][day_date]

            present = sum(
                day.get(student) == "PRESENT"
                for student in STUDENTS
            )

            leave = sum(
                day.get(student) == "LEAVE"
                for student in STUDENTS
            )

            absent = sum(
                day.get(student) == "ABSENT"
                for student in STUDENTS
            )

            with st.expander(
                f"{format_date(day_date)}   "
                f"• P {present} "
                f"• L {leave} "
                f"• A {absent}"
            ):

                for student in STUDENTS:

                    status = day.get(
                        student,
                        ""
                    )

                    if status == "PRESENT":
                        icon = "🟢"

                    elif status == "LEAVE":
                        icon = "🟠"

                    elif status == "ABSENT":
                        icon = "🔴"

                    else:
                        icon = "⚪"

                    st.write(
                        f"{icon} **{student}** — "
                        f"{status or 'NOT SET'}"
                    )


# =========================================================
# TOTAL FINE
# =========================================================

elif st.session_state.page == "Total Fine":

    st.subheader("💳 Total Fine")

    total_fines = get_total_fines()
    remaining_fines = get_remaining_fines()
    payments = get_paid_amounts()


    # Overall summary
    total = sum(
        total_fines.values()
    )

    paid = sum(
        payments.get(
            student,
            0
        )
        for student in STUDENTS
    )

    remaining = sum(
        remaining_fines.values()
    )


    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Total",
            f"{total} Tk"
        )

    with c2:
        st.metric(
            "Paid",
            f"{paid} Tk"
        )

    with c3:
        st.metric(
            "Due",
            f"{remaining} Tk"
        )


    st.write("")


    for student in STUDENTS:

        total_student = total_fines.get(
            student,
            0
        )

        paid_student = payments.get(
            student,
            0
        )

        due_student = remaining_fines.get(
            student,
            0
        )

        with st.container(border=True):

            st.markdown(
                f"### 👤 {student}"
            )

            a, b, c = st.columns(3)

            with a:
                st.write(
                    f"Total\n"
                    f"**{total_student} Tk**"
                )

            with b:
                st.write(
                    f"Paid\n"
                    f"**{paid_student} Tk**"
                )

            with c:
                st.write(
                    f"Due\n"
                    f"**{due_student} Tk**"
                )


# =========================================================
# COLLECT FEE
# =========================================================

elif st.session_state.page == "Collect Fee":

    st.subheader("💵 Collect / Pay Fee")

    st.info(
        "কেউ বকেয়া টাকা পরিশোধ করলে "
        "সেই টাকা মোট বকেয়া থেকে "
        "স্বয়ংক্রিয়ভাবে কমে যাবে।"
    )


    student = st.selectbox(
        "Select Student",
        STUDENTS
    )


    remaining = get_remaining_fines()

    current_due = remaining.get(
        student,
        0
    )


    st.metric(
        "Current Due",
        f"{current_due} Tk"
    )


    amount = st.number_input(
        "Payment Amount",
        min_value=0,
        max_value=max(
            current_due,
            0
        ),
        value=0,
        step=10
    )


    if st.button(
        "💳 Confirm Payment",
        use_container_width=True
    ):

        if current_due <= 0:

            st.success(
                f"{student}-এর কোনো বকেয়া নেই।"
            )

        elif amount <= 0:

            st.warning(
                "Payment amount দিন।"
            )

        else:

            data.setdefault(
                "payments",
                {}
            )

            old_payment = data[
                "payments"
            ].get(
                student,
                0
            )

            data["payments"][
                student
            ] = old_payment + amount

            save_data(data)

            st.success(
                f"{student}-এর কাছ থেকে "
                f"{amount} Tk নেওয়া হয়েছে।"
            )

            st.rerun()


# =========================================================
# BOTTOM INFO
# =========================================================

st.write("")
st.write("")

st.caption(
    "Attendance E-Khata • Mobile Web App"
    )
