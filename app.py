import streamlit as st
from supabase import create_client
import pandas as pd
import math

# 1. Setup & Connection
SUB_GOAL = 0.60
TOTAL_GOAL = 0.75
supabase = create_client("https://sxxdzlsmsgopybwzjbnc.supabase.co", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN4eGR6bHNtc2dvcHlid3pqYm5jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3ODQyOTA2NCwiZXhwIjoyMDk0MDA1MDY0fQ.druJl5ZaVBqr9xQpnN1AQ0NPQgbYjNgCYq7WDaCtbsk")

st.set_page_config(page_title="Attendance Pro", layout="wide")
st.title("📊 Attendance Tracking System")

# 2. Input Section
subjects = ["Data Science", "Computer Networks", "AI/ML", "Cloud Computing"]
with st.sidebar:
    st.header("Mark Attendance")
    selected_sub = st.selectbox("Subject", subjects)
    col1, col2 = st.columns(2)
    if col1.button("✅ Present"):
        supabase.table("attendance_logs").insert({"subject_name": selected_sub, "status": "Present"}).execute()
    if col2.button("❌ Absent"):
        supabase.table("attendance_logs").insert({"subject_name": selected_sub, "status": "Absent"}).execute()

# 3. Data Processing & Logic
data = supabase.table("attendance_logs").select("*").execute()
df = pd.DataFrame(data.data)

if not df.empty:
    df['created_at'] = pd.to_datetime(df['created_at'])
    
    # Per Subject Analysis
    results = []
    for sub in subjects:
        sub_df = df[df['subject_name'] == sub]
        p = len(sub_df[sub_df['status'] == 'Present'])
        a = len(sub_df[sub_df['status'] == 'Absent'])
        total = p + a
        current_pct = p / total if total > 0 else 0
        
        if current_pct >= SUB_GOAL:
            val = math.floor((p - (SUB_GOAL * total)) / SUB_GOAL)
            status_text = f"🟢 Safe: Can miss {val} classes"
        else:
            val = math.ceil(((SUB_GOAL * total) - p) / (1 - SUB_GOAL))
            status_text = f"🔴 Danger: Attend {val} more"
            
        results.append({"Subject": sub, "Attendance": f"{current_pct:.1%}", "Instruction": status_text})

    # 4. Display Dashboard
    st.subheader("Current Standing")
    st.table(results)
    
    # Monthly Report Logic
    st.subheader("📅 Monthly Summary")
    df['Month'] = df['created_at'].dt.strftime('%Y-%m')
    report = df.groupby(['Month', 'status']).size().unstack(fill_value=0)
    st.bar_chart(report)
