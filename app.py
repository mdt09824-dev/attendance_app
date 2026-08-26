import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

# File to store data
DATA_FILE = "attendance_data.json"

# Default data structure
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "students": [],
        "attendance": {},
        "payments": [],
        "fees": {},  # Format: {"Student Name": {"Month_Year": "Paid"/"Due"}}
        "settings": {
            "default_fine": 10,
            "special_fine": 50,
            "monthly_fee": 500
        }
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

data = load_data()

st.set_page_config(page_title="Private Attendance & Fee E-Khata", page_icon="📚", layout="wide")

# Custom CSS for professional look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 6px; font-weight: bold; }
    .metric-card { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); text-align: center; }
    </style>
""", unsafe_allow_html=True)

st.title("📚 Private Attendance & Fee E-Khata")
st.markdown("শিক্ষক মহাশয়ের জন্য ডিজিটাল হাজিরা এবং মাসিক বেতন ম্যানেজমেন্ট সিস্টেম")

# Sidebar navigation
menu = st.sidebar.selectbox("মেনু নির্বাচন করুন", [
    "🏠 ড্যাশবোর্ড (Dashboard)",
    "📝 আজকের হাজিরা (Attendance)",
    "💰 মাসিক বেতন ম্যানেজমেন্ট (Tuition Fees)",
    "💸 ফাইন কালেকশন (Fine Collection)",
    "👥 মেম্বার ম্যানেজ (Manage Students)",
    "⚙️ সেটিংস ও রিসেট (Settings)"
])

# 1. Dashboard
if menu == "🏠 ড্যাশবোর্ড (Dashboard)":
    st.header("📊 সার্বিক ড্যাশবোর্ড সামারি")
    
    total_students = len(data["students"])
    
    # Calculate Total Fines Due
    total_fine_due = 0
    for student in data["students"]:
        student_fines = sum([entry.get("amount", 0) for entry in data.get("payments", []) if entry["student"] == student and not entry.get("paid", False)])
        total_fine_due += student_fines

    # Calculate Total Fee Due for current month
    current_month_str = datetime.now().strftime("%B %Y")
    monthly_fee = data["settings"].get("monthly_fee", 500)
    total_fee_due = 0
    for student in data["students"]:
        student_fee_status = data["fees"].get(student, {}).get(current_month_str, "Due")
        if student_fee_status == "Due":
            total_fee_due += monthly_fee

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="metric-card"><h3>মোট শিক্ষার্থী</h3><h2>{total_students} জন</h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><h3>বকেয়া ফাইন</h3><h2 style="color: #d9534f;">{total_fine_due} টাকা</h2></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><h3>এই মাসের বকেয়া বেতন</h3><h2 style="color: #f0ad4e;">{total_fee_due} টাকা</h2></div>', unsafe_allow_html=True)

    st.divider()
    st.subheader("📋 শিক্ষার্থীদের তালিকা")
    if data["students"]:
        df_students = pd.DataFrame({"শিক্ষার্থীর নাম": data["students"]})
        st.dataframe(df_students, use_container_width=True)
    else:
        st.info("এখনো কোনো শিক্ষার্থী যুক্ত করা হয়নি। 'মেম্বার ম্যানেজ' অপশন থেকে শিক্ষার্থী যোগ করুন।")

# 2. Attendance
elif menu == "📝 আজকের হাজিরা (Attendance)":
    st.header("📝 উপস্থিতি এবং ফাইন এন্ট্রি")
    
    if not data["students"]:
        st.warning("প্রথমে 'মেম্বার ম্যানেজ' থেকে শিক্ষার্থী যোগ করুন।")
    else:
        selected_date = st.date_input("তারিখ নির্বাচন করুন", datetime.today())
        date_str = selected_date.strftime("%Y-%m-%d")
        
        if date_str not in data["attendance"]:
            data["attendance"][date_str] = {s: "Present" for s in data["students"]}
            
        st.info(f"তারিখ: {date_str} - হাজিরা ও ফাইন মার্ক করুন")
        
        with st.form("attendance_form"):
            updated_attendance = {}
            fines_to_add = []
            
            for student in data["students"]:
                col1, col2, col3 = st.columns([3, 2, 2])
                with col1:
                    st.write(f"**{student}**")
                with col2:
                    current_status = data["attendance"][date_str].get(student, "Present")
                    status = st.selectbox("স্ট্যাটাস", ["Present", "Absent", "Leave"], index=["Present", "Absent", "Leave"].index(current_status), key=f"status_{student}")
                    updated_attendance[student] = status
                with col3:
                    fine_type = st.selectbox("ফাইন", ["কোনোটি না", "সাধারণ ফাইন", "বিশেষ ফাইন"], key=f"fine_{student}")
                    if fine_type == "সাধারণ ফাইন":
                        fines_to_add.append({"student": student, "amount": data["settings"]["default_fine"], "reason": f"Absent on {date_str}", "date": date_str, "paid": False})
                    elif fine_type == "বিশেষ ফাইন":
                        fines_to_add.append({"student": student, "amount": data["settings"]["special_fine"], "reason": f"Special Fine on {date_str}", "date": date_str, "paid": False})
            
            submitted = st.form_submit_button("হাজিরা ও ফাইন সেভ করুন")
            if submitted:
                data["attendance"][date_str] = updated_attendance
                for fine in fines_to_add:
                    data["payments"].append(fine)
                save_data(data)
                st.success("হাজিরা সফলভাবে সংরক্ষিত হয়েছে!")

# 3. Tuition Fee Management (The new star feature)
elif menu == "💰 মাসিক বেতন ম্যানেজমেন্ট (Tuition Fees)":
    st.header("💰 মাসিক টিউশন ফি ম্যানেজমেন্ট")
    
    if not data["students"]:
        st.warning("প্রথমে শিক্ষার্থী যোগ করুন।")
    else:
        # Month selector
        months = ["January 2026", "February 2026", "March 2026", "April 2026", "May 2026", "June 2026", 
                  "July 2026", "August 2026", "September 2026", "October 2026", "November 2026", "December 2026"]
        current_default_month = datetime.now().strftime("%B %Y")
        if current_default_month not in months:
            months.append(current_default_month)
            
        selected_month = st.selectbox("মাস নির্বাচন করুন", months, index=months.index(current_default_month) if current_default_month in months else 0)
        monthly_fee_amount = data["settings"].get("monthly_fee", 500)
        
        st.markdown(f"**নির্ধারিত মাসিক ফি:** {monthly_fee_amount} টাকা")
        
        # Display Fee Table
        fee_data = []
        for student in data["students"]:
            status = data["fees"].get(student, {}).get(selected_month, "Due")
            fee_data.append({"শিক্ষার্থীর নাম": student, "মাস": selected_month, "পরিমাণ": f"{monthly_fee_amount} Tk", "স্ট্যাটাস": status})
            
        df_fee = pd.DataFrame(fee_data)
        st.dataframe(df_fee, use_container_width=True)
        
        st.divider()
        st.subheader("বেতন পরিশোধ আপডেট করুন (Pay Fee)")
        with st.form("fee_update_form"):
            pay_student = st.selectbox("শিক্ষার্থী নির্বাচন করুন", data["students"])
            new_status = st.selectbox("বেতনের অবস্থা", ["Paid", "Due"])
            submit_fee = st.form_submit_button("বেতন স্ট্যাটাস আপডেট করুন")
            
            if submit_fee:
                if pay_student not in data["fees"]:
                    data["fees"][pay_student] = {}
                data["fees"][pay_student][selected_month] = new_status
                save_data(data)
                st.success(f"{pay_student}-এর {selected_month} মাসের বেতন স্ট্যাটাস '{new_status}' করা হয়েছে!")

# 4. Fine Collection
elif menu == "💸 ফাইন কালেকশন (Fine Collection)":
    st.header("💸 বকেয়া ফাইন কালেকশন")
    
    unpaid_fines = [i for i, entry in enumerate(data.get("payments", [])) if not entry.get("paid", False)]
    
    if not unpaid_fines:
        st.success("কারো কোনো বকেয়া ফাইন নেই! 🎉")
    else:
        st.subheader("বকেয়া ফাইনের তালিকা")
        display_list = []
        for idx in unpaid_fines:
            entry = data["payments"][idx]
            display_list.append({
                "Index": idx,
                "শিক্ষার্থী": entry["student"],
                "কারণ": entry["reason"],
                "পরিমাণ": f"{entry['amount']} Tk",
                "তারিখ": entry["date"]
            })
        st.dataframe(pd.DataFrame(display_list), use_container_width=True)
        
        with st.form("collect_fine_form"):
            selected_idx = st.selectbox("পরিশোধ হয়েছে এমন এন্ট্রি সিলেক্ট করুন (Index নম্বর অনুযায়ী)", unpaid_fines, format_func=lambda x: f"ID {x}: {data['payments'][x]['student']} - {data['payments'][x]['amount']} Tk ({data['payments'][x]['reason']})")
            collect_btn = st.form_submit_button("টাকা আদায় হিসেবে মার্ক করুন (Paid)")
            
            if collect_btn:
                data["payments"][selected_idx]["paid"] = True
                save_data(data)
                st.success("ফাইনের টাকা আদায় হিসেবে আপডেট করা হয়েছে!")

# 5. Manage Students
elif menu == "👥 মেম্বার ম্যানেজ (Manage Students)":
    st.header("👥 শিক্ষার্থী যোগ বা বাদ দিন")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("নতুন শিক্ষার্থী যোগ করুন")
        with st.form("add_student_form"):
            new_name = st.text_input("শিক্ষার্থীর নাম")
            add_btn = st.form_submit_button("যোগ করুন")
            if add_btn:
                if new_name and new_name not in data["students"]:
                    data["students"].append(new_name)
                    save_data(data)
                    st.success(f"'{new_name}' সফলভাবে যুক্ত হয়েছে!")
                elif new_name in data["students"]:
                    st.warning("এই নামে ইতিমধ্যে শিক্ষার্থী রয়েছে।")
                else:
                    st.error("দয়া করে নাম লিখুন।")
                    
    with col2:
        st.subheader("শিক্ষার্থী বাদ দিন")
        with st.form("remove_student_form"):
            if data["students"]:
                rem_name = st.selectbox("শিক্ষার্থী নির্বাচন করুন", data["students"])
                rem_btn = st.form_submit_button("বাদ দিন")
                if rem_btn:
                    data["students"].remove(rem_name)
                    save_data(data)
                    st.success(f"'{rem_name}' তালিকা থেকে বাদ দেওয়া হয়েছে!")
            else:
                st.info("তালিকা খালি আছে।")

# 6. Settings
elif menu == "⚙️ সেটিংস ও রিসেট (Settings)":
    st.header("⚙️ অ্যাপ সেটিংস ও ফাইন কনফিগারেশন")
    
    with st.form("settings_form"):
        def_fine = st.number_input("সাধারণ ফাইন (টাকা)", value=data["settings"].get("default_fine", 10))
        spec_fine = st.number_input("বিশেষ ফাইন (টাকা)", value=data["settings"].get("special_fine", 50))
        m_fee = st.number_input("মাসিক টিউশন ফি (টাকা)", value=data["settings"].get("monthly_fee", 500))
        
        save_settings = st.form_submit_button("সেটিংস সেভ করুন")
        if save_settings:
            data["settings"]["default_fine"] = def_fine
            data["settings"]["special_fine"] = spec_fine
            data["settings"]["monthly_fee"] = m_fee
            save_data(data)
            st.success("সেটিংস সফলভাবে আপডেট হয়েছে!")
            
    st.divider()
    if st.button("⚠️ সমস্ত ডেটা রিসেট করুন (Reset All Data)", type="primary"):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        st.success("সব ডেটা সফলভাবে মুছে ফেলা হয়েছে! অ্যাপ রিলোড করুন।")
