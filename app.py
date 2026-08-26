import os
import json
from datetime import datetime, date
import streamlit as st

# =========================================================
# CONFIG
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

st.set_page_config(
    page_title="Attendance E-Khata",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =========================================================
# CSS - MOBILE APP STYLE
# =========================================================

st.markdown("""
<style>

* {
    box-sizing: border-box;
}

html, body, [class*="css"] {
    font-family: Arial, Helvetica, sans-serif;
}

body {
    background: #f6f8ff;
}

.stApp {
    background: #f7f8fc;
}

/* Hide Streamlit default UI */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

/* Main mobile container */
.block-container {
    max-width: 460px !important;
    padding: 0 12px 90px 12px !important;
}

/* Remove excessive gaps */
.element-container {
    margin-bottom: 0 !important;
}

/* ================= HEADER ================= */

.app-header {
    margin: -1px -12px 15px -12px;
    padding: 20px 20px 24px 20px;
    background: linear-gradient(
        135deg,
        #087cf5 0%,
        #3158e8 48%,
        #7a32ed 100%
    );
    color: white;
    border-radius: 0 0 28px 28px;
    box-shadow: 0 8px 25px rgba(57, 82, 230, 0.25);
}

.header-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.header-left {
    display: flex;
    align-items: center;
    gap: 14px;
}

.menu-icon {
    font-size: 28px;
    line-height: 1;
}

.app-title {
    font-size: 24px;
    font-weight: 700;
}

.bell {
    font-size: 26px;
    position: relative;
}

.bell-badge {
    position: absolute;
    right: -7px;
    top: -8px;
    width: 20px;
    height: 20px;
    background: #ff3b30;
    border-radius: 50%;
    font-size: 12px;
    display: flex;
    justify-content: center;
    align-items: center;
}

/* ================= DATE CARD ================= */

.date-card {
    background: white;
    border: 1px solid #e4e8f2;
    border-radius: 18px;
    padding: 16px;
    margin-bottom: 14px;
    box-shadow: 0 4px 14px rgba(40, 55, 90, .06);
}

.date-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.date-left {
    display: flex;
    align-items: center;
    gap: 13px;
}

.calendar-icon {
    width: 52px;
    height: 52px;
    border-radius: 50%;
    background: #eaf1ff;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 26px;
}

.date-label {
    font-size: 12px;
    color: #778096;
    margin-bottom: 4px;
}

.date-value {
    font-size: 18px;
    font-weight: 700;
    color: #202840;
}

.count-row {
    display: flex;
    gap: 14px;
    margin-top: 7px;
    font-size: 13px;
}

.count-present {
    color: #22a060;
}

.count-leave {
    color: #ec9418;
}

.count-absent {
    color: #ed3944;
}

.count-notset {
    color: #666f80;
}

.change-date {
    border: 1px solid #b9c9ec;
    color: #2961d7;
    background: #fff;
    border-radius: 9px;
    padding: 11px 12px;
    font-size: 12px;
    font-weight: 600;
}

/* ================= STAT CARDS ================= */

.stat-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 9px;
    margin-bottom: 15px;
}

.stat-card {
    min-height: 145px;
    border-radius: 14px;
    padding: 13px 10px;
    position: relative;
    border: 1px solid;
}

.stat-title {
    font-size: 13px;
    color: #30394f;
    margin-bottom: 13px;
}

.stat-number {
    font-size: 28px;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 12px;
}

.stat-sub {
    font-size: 12px;
    color: #30394f;
}

.stat-icon {
    position: absolute;
    right: 10px;
    bottom: 12px;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 19px;
}

.present-card {
    background: #eefaf3;
    border-color: #d6efdf;
}

.present-card .stat-number {
    color: #159447;
}

.present-card .stat-icon {
    background: #20a35b;
}

.leave-card {
    background: #fff8eb;
    border-color: #f5e5c5;
}

.leave-card .stat-number {
    color: #e78d0e;
}

.leave-card .stat-icon {
    background: #f39a18;
}

.absent-card {
    background: #fff0f2;
    border-color: #f3d7dc;
}

.absent-card .stat-number {
    color: #e93440;
}

.absent-card .stat-icon {
    background: #eb3744;
}

.fee-card {
    background: #eef4ff;
    border-color: #d8e3f8;
}

.fee-card .stat-number {
    color: #2462d5;
    font-size: 23px;
}

.fee-after {
    color: #159447;
    font-size: 17px;
    font-weight: 700;
    margin-top: -5px;
}

/* ================= FEE BOX ================= */

.fee-box {
    background: linear-gradient(135deg, #f6f8ff, #edf3ff);
    border: 1px solid #bdccec;
    border-radius: 17px;
    padding: 18px;
    margin-bottom: 16px;
}

.fee-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.fee-side {
    display: flex;
    align-items: center;
    gap: 12px;
}

.wallet {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: linear-gradient(135deg, #654ce8, #8961ef);
    display: flex;
    justify-content: center;
    align-items: center;
    color: white;
    font-size: 23px;
}

.fee-label {
    font-size: 13px;
    color: #343d52;
}

.fee-amount {
    font-size: 27px;
    font-weight: 700;
    color: #202a45;
}

.arrow {
    font-size: 34px;
    color: #7b8291;
}

.after-payment {
    color: #1a9a54;
}

.collect-button {
    margin-top: 15px;
    background: linear-gradient(
        90deg,
        #086ff4,
        #6b35ef
    );
    color: white;
    text-align: center;
    padding: 12px;
    border-radius: 9px;
    font-size: 15px;
    font-weight: 600;
}

/* ================= SECTION TITLE ================= */

.section-title {
    font-size: 17px;
    font-weight: 700;
    color: #273049;
    margin: 18px 3px 10px;
}

/* ================= STUDENT LIST ================= */

.student-header {
    display: grid;
    grid-template-columns: 1.45fr .85fr 1.45fr;
    padding: 10px 9px;
    color: #37415a;
    background: #f1f4fb;
    border-radius: 12px 12px 0 0;
    font-size: 12px;
}

.student-row {
    display: grid;
    grid-template-columns: 1.45fr .85fr 1.45fr;
    align-items: center;
    padding: 9px 7px;
    background: white;
    border-bottom: 1px solid #edf0f5;
}

.student-name {
    display: flex;
    align-items: center;
    gap: 7px;
    font-size: 14px;
    font-weight: 600;
    color: #273149;
}

.avatar {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    background: #e9eef8;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
}

.status-badge {
    display: inline-block;
    padding: 6px 5px;
    border-radius: 7px;
    font-size: 10px;
    font-weight: 700;
    text-align: center;
}

.status-present {
    background: #e9f8ef;
    color: #229653;
}

.status-leave {
    background: #fff4df;
    color: #e99216;
}

.status-absent {
    background: #ffecef;
    color: #e73543;
}

.status-empty {
    background: #f1f3f6;
    color: #777f8e;
}

/* Streamlit buttons */
.stButton > button {
    border-radius: 8px !important;
    min-height: 34px !important;
    padding: 2px 5px !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    border: 1px solid #dce2ec !important;
    background: white !important;
}

.stButton > button:hover {
    border-color: #6b7fe8 !important;
    color: #315ee4 !important;
}

/* Action button columns */
.action-wrap {
    display: flex;
    gap: 4px;
}

/* ================= BOTTOM NAV ================= */

.bottom-nav {
    position: fixed;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: min(460px, 100%);
    height: 72px;
    background: rgba(255,255,255,.97);
    border-top: 1px solid #e2e5ec;
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    z-index: 9999;
    box-shadow: 0 -5px 20px rgba(20,30,60,.08);
}

.nav-item {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 5px;
    color: #60697b;
    font-size: 10px;
    font-weight: 600;
}

.nav-icon {
    font-size: 23px;
}

.nav-active {
    color: #1765df;
}

/* ================= FORMS ================= */

.stSelectbox > div > div,
.stNumberInput > div > div > input,
.stDateInput > div > div > input {
    border-radius: 10px !important;
}

.success-box {
    background: #eaf9ef;
    border: 1px solid #c8ecd5;
    color: #18894a;
    padding: 12px;
    border-radius: 10px;
}

/* ================= DESKTOP ================= */

@media (min-width: 700px) {
    .block-container {
        max-width: 480px !important;
    }
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# DATA FUNCTIONS
# =========================================================

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

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        data.setdefault("days", {})
        data.setdefault(
            "initial_fine",
            INITIAL_FINE.copy()
        )
        data.setdefault(
            "payments",
            {}
        )

        for day_data in data["days"].values():

            for name in STUDENTS:
                day_data.setdefault(
                    name,
                    ""
                )

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


# =========================================================
# SESSION DATA
# =========================================================

if "data" not in st.session_state:

    st.session_state.data = load_data()


data = st.session_state.data


# =========================================================
# CREATE TODAY
# =========================================================

if today_str() not in data["days"]:

    data["days"][today_str()] = blank_day()

    # Default example
    if "Nirob" in STUDENTS:
        data["days"][today_str()]["Nirob"] = "LEAVE"

    save_data(data)


# =========================================================
# FINE CALCULATION
# =========================================================

def get_total_fines():

    fines = {
        s: int(
            data["initial_fine"].get(s, 0)
        )
        for s in STUDENTS
    }

    for day_data in data["days"].values():

        for student, status in day_data.items():

            if status == "ABSENT":

                fines[student] = (
                    fines.get(student, 0)
                    + FINE_PER_ABSENT
                )

    return fines


def get_remaining_fines():

    total_fines = get_total_fines()

    payments = data.get(
        "payments",
        {}
    )

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
# HEADER
# =========================================================

st.markdown("""
<div class="app-header">

    <div class="header-row">

        <div class="header-left">

            <div class="menu-icon">☰</div>

            <div class="app-title">
                Attendance E-Khata
            </div>

        </div>

        <div class="bell">

            🔔

            <div class="bell-badge">
                3
            </div>

        </div>

    </div>

</div>
""", unsafe_allow_html=True)


# =========================================================
# NAVIGATION
# =========================================================

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"


nav_cols = st.columns(4)

with nav_cols[0]:

    if st.button(
        "🏠\nDashboard",
        key="nav_dashboard",
        use_container_width=True
    ):
        st.session_state.page = "Dashboard"
        st.rerun()

with nav_cols[1]:

    if st.button(
        "◷\nHistory",
        key="nav_history",
        use_container_width=True
    ):
        st.session_state.page = "History"
        st.rerun()

with nav_cols[2]:

    if st.button(
        "💳\nTotal Fine",
        key="nav_fine",
        use_container_width=True
    ):
        st.session_state.page = "Total Fine"
        st.rerun()

with nav_cols[3]:

    if st.button(
        "•••\nMore",
        key="nav_more",
        use_container_width=True
    ):
        st.session_state.page = "Collect Fee"
        st.rerun()


# =========================================================
# DASHBOARD
# =========================================================

if st.session_state.page == "Dashboard":

    # -----------------------------------------
    # DATE
    # -----------------------------------------

    selected_date = st.date_input(
        "Date",
        value=datetime.strptime(
            today_str(),
            "%Y-%m-%d"
        ).date(),
        label_visibility="collapsed"
    )

    current_date = selected_date.strftime(
        "%Y-%m-%d"
    )

    if current_date not in data["days"]:

        data["days"][current_date] = blank_day()
        save_data(data)

    day_data = data["days"][current_date]

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

    remaining = get_remaining_fines()

    total_due = sum(
        remaining.values()
    )

    total_all_fines = sum(
        get_total_fines().values()
    )

    # -----------------------------------------
    # DATE CARD
    # -----------------------------------------

    st.markdown(f"""
    <div class="date-card">

        <div class="date-row">

            <div class="date-left">

                <div class="calendar-icon">
                    📅
                </div>

                <div>

                    <div class="date-label">
                        Date
                    </div>

                    <div class="date-value">
                        {format_date(current_date)}
                    </div>

                    <div class="count-row">

                        <span class="count-present">
                            Present: {present}
                        </span>

                        <span class="count-leave">
                            Leave: {leave}
                        </span>

                        <span class="count-absent">
                            Absent: {absent}
                        </span>

                    </div>

                </div>

            </div>

            <div class="change-date">
                📅 Change Date
            </div>

        </div>

    </div>
    """, unsafe_allow_html=True)


    # -----------------------------------------
    # STAT CARDS
    # -----------------------------------------

    st.markdown(f"""

    <div class="stat-grid">

        <div class="stat-card present-card">

            <div class="stat-title">
                Present
            </div>

            <div class="stat-number">
                {present}
            </div>

            <div class="stat-sub">
                Students
            </div>

            <div class="stat-icon">
                ✓
            </div>

        </div>


        <div class="stat-card leave-card">

            <div class="stat-title">
                Leave
            </div>

            <div class="stat-number">
                {leave}
            </div>

            <div class="stat-sub">
                Students
            </div>

            <div class="stat-icon">
                👤
            </div>

        </div>


        <div class="stat-card absent-card">

            <div class="stat-title">
                Absent
            </div>

            <div class="stat-number">
                {absent}
            </div>

            <div class="stat-sub">
                Students
            </div>

            <div class="stat-icon">
                ×
            </div>

        </div>


        <div class="stat-card fee-card">

            <div class="stat-title">
                Total Fee
            </div>

            <div class="stat-number">
                {total_all_fines} Tk
            </div>

            <div class="stat-sub">
                After Payment
            </div>

            <div class="fee-after">
                {total_due} Tk
            </div>

            <div class="stat-icon">
                💳
            </div>

        </div>

    </div>

    """, unsafe_allow_html=True)


    # -----------------------------------------
