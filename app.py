import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import date

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Tea Leaf Business Tracker", page_icon="🍃", layout="wide")

# --- 2. PASSWORD PROTECTION ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.title("🔒 Private Tea Business Login")
        pwd = st.text_input("Enter Admin Password:", type="password")
        if st.button("Login"):
            # Checks against the secret password you set in Streamlit Cloud
            if pwd == st.secrets["APP_PASSWORD"]:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("❌ Incorrect password.")
        return False
    return True

if not check_password():
    st.stop()

# --- 3. DATA STORAGE SETUP ---
DATA_FILE = "tea_records.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        # Sample starting data so your charts look great immediately
        sample_data = pd.DataFrame([
            {"Date": "2026-11-01", "Block/Farm": "Block A", "Pluckers": 6, "Green Leaf (kg)": 320.0, "Rate (KES/kg)": 25.0, "Plucking & Transport Cost (KES)": 3200.0},
            {"Date": "2026-11-05", "Block/Farm": "Block B", "Pluckers": 8, "Green Leaf (kg)": 450.0, "Rate (KES/kg)": 25.0, "Plucking & Transport Cost (KES)": 4500.0},
            {"Date": "2026-11-10", "Block/Farm": "Block A", "Pluckers": 7, "Green Leaf (kg)": 390.0, "Rate (KES/kg)": 26.0, "Plucking & Transport Cost (KES)": 3800.0},
            {"Date": "2026-11-15", "Block/Farm": "Block C", "Pluckers": 9, "Green Leaf (kg)": 510.0, "Rate (KES/kg)": 26.0, "Plucking & Transport Cost (KES)": 4900.0},
        ])
        sample_data.to_csv(DATA_FILE, index=False)
        return sample_data

df = load_data()

# Calculate Revenue & Net Profit
df["Gross Revenue (KES)"] = df["Green Leaf (kg)"] * df["Rate (KES/kg)"]
df["Net Profit (KES)"] = df["Gross Revenue (KES)"] - df["Plucking & Transport Cost (KES)"]
df["Kg per Plucker"] = (df["Green Leaf (kg)"] / df["Pluckers"]).round(1)

# --- 4. SIDEBAR: ADD NEW HARVEST ENTRY ---
st.sidebar.header("➕ Log New Harvest")
with st.sidebar.form("entry_form", clear_on_submit=True):
    entry_date = st.date_input("Harvest Date", date.today())
    farm_block = st.selectbox("Farm / Block", ["Block A", "Block B", "Block C", "Outgrowers"])
    pluckers = st.number_input("Number of Pluckers", min_value=1, value=5, step=1)
    weight_kg = st.number_input("Green Leaf Weight (kg)", min_value=1.0, value=250.0, step=5.0)
    rate_kes = st.number_input("Factory Rate (KES/kg)", min_value=1.0, value=25.0, step=0.5)
    expenses_kes = st.number_input("Labor & Transport Expenses (KES)", min_value=0.0, value=2500.0, step=100.0)
    
    submitted = st.form_submit_button("Save Record")
    if submitted:
        new_row = pd.DataFrame([{
            "Date": str(entry_date),
            "Block/Farm": farm_block,
            "Pluckers": pluckers,
            "Green Leaf (kg)": weight_kg,
            "Rate (KES/kg)": rate_kes,
            "Plucking & Transport Cost (KES)": expenses_kes
        }])
        df_updated = pd.concat([df.drop(columns=["Gross Revenue (KES)", "Net Profit (KES)", "Kg per Plucker"]), new_row], ignore_index=True)
        df_updated.to_csv(DATA_FILE, index=False)
        st.sidebar.success("✅ Harvest saved!")
        st.rerun()

if st.sidebar.button("🚪 Logout"):
    st.session_state["authenticated"] = False
    st.rerun()

# --- 5. MAIN DASHBOARD & KPIs ---
st.title("🍃 Tea Leaves Business Performance Tracker")
st.markdown("Monitor green leaf harvests, plucker productivity, expenses, and net profit.")

total_kg = df["Green Leaf (kg)"].sum()
total_rev = df["Gross Revenue (KES)"].sum()
total_exp = df["Plucking & Transport Cost (KES)"].sum()
total_profit = df["Net Profit (KES)"].sum()
avg_productivity = df["Kg per Plucker"].mean()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Harvest", f"{total_kg:,.1f} kg")
col2.metric("Gross Revenue", f"KES {total_rev:,.0f}")
col3.metric("Total Expenses", f"KES {total_exp:,.0f}")
col4.metric("Net Profit", f"KES {total_profit:,.0f}")
col5.metric("Avg Yield / Plucker", f"{avg_productivity:.1f} kg")

st.divider()

# --- 6. CHARTS & GRAPHS ---
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("📈 Harvest Weight Trend (kg)")
    df_sorted = df.sort_values("Date")
    fig_line = px.line(df_sorted, x="Date", y="Green Leaf (kg)", color="Block/Farm", markers=True)
    st.plotly_chart(fig_line, use_container_width=True)

with chart_col2:
    st.subheader("💰 Revenue vs. Expenses by Block")
    block_summary = df.groupby("Block/Farm")[["Gross Revenue (KES)", "Plucking & Transport Cost (KES)", "Net Profit (KES)"]].sum().reset_index()
    fig_bar = px.bar(block_summary, x="Block/Farm", y=["Gross Revenue (KES)", "Plucking & Transport Cost (KES)", "Net Profit (KES)"], barmode="group")
    st.plotly_chart(fig_bar, use_container_width=True)

# --- 7. DATA TABLE & DOWNLOAD ---
st.subheader("📋 Harvest Ledger")
st.dataframe(df.sort_values("Date", ascending=False), use_container_width=True)

csv_download = df.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download Ledger as CSV (Excel)", data=csv_download, file_name="tea_business_report.csv", mime="text/csv")
