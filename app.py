import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import calendar
import os
from datetime import date

# ============================================================
# S&L TEA VENTURES | BUSINESS PERFORMANCE DASHBOARD
# ============================================================

st.set_page_config(
    page_title="S&L Tea Ventures | Dashboard",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- BRAND COLOURS -------------------------

NAVY = "#0B2850"
BLUE = "#1769AA"
LIGHT_BLUE = "#EAF3FF"
GREEN = "#20A779"
ORANGE = "#F39C35"
RED = "#DF5260"
PURPLE = "#805AD5"
WHITE = "#FFFFFF"
MONTHS = list(calendar.month_name)[1:]
DATA_FILE = "sl_tea_records.csv"

# -------------------- CUSTOM CSS ----------------------------

st.markdown("""
<style>
.stApp {
    background-color: #F3F6FB;
    color: #14243A;
}
.block-container {
    padding-top: 1.1rem;
    padding-bottom: 2rem;
    max-width: 1600px;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#092448,#124477);
}
[data-testid="stSidebar"] * {
    color: white !important;
}
[data-testid="stSidebar"] .stRadio label {
    padding: 9px;
    border-radius: 7px;
}
.hero {
    background: linear-gradient(110deg,#092448,#1769AA);
    padding: 20px 24px;
    border-radius: 13px;
    color: white;
    margin-bottom: 17px;
    box-shadow: 0 5px 16px rgba(9,36,72,.16);
}
.hero h1 {
    color: white !important;
    font-size: 27px;
    margin: 0;
}
.hero p {
    color: #D8E9FF;
    margin: 5px 0 0 0;
    font-size: 13px;
}
.section-title {
    background: #0B2850;
    color: white;
    padding: 10px 14px;
    border-radius: 7px;
    font-weight: 700;
    font-size: 14px;
    margin: 13px 0 10px 0;
}
.metric-card {
    background: white;
    padding: 13px 14px;
    border-radius: 10px;
    border: 1px solid #DCE7F4;
    border-left: 4px solid #1769AA;
    min-height: 90px;
    box-shadow: 0 2px 8px rgba(20,50,90,.04);
}
.metric-label {
    color: #60758D;
    font-size: 11px;
    font-weight: 600;
}
.metric-value {
    color: #0B2850;
    font-size: 22px;
    font-weight: 750;
    margin-top: 5px;
}
.metric-sub {
    color: #8495A8;
    font-size: 10px;
}
.info-card {
    background: white;
    border: 1px solid #DCE7F4;
    padding: 13px;
    border-radius: 10px;
    margin-bottom: 9px;
}
div[data-testid="stMetric"] {
    background: white;
    padding: 12px;
    border-radius: 10px;
    border: 1px solid #DCE7F4;
    border-left: 4px solid #1769AA;
}
div[data-testid="stMetricLabel"] {
    color: #60758D;
}
div[data-testid="stMetricValue"] {
    color: #0B2850;
}
.stButton > button,
.stDownloadButton > button {
    background: #1769AA;
    color: white;
    border: none;
    border-radius: 7px;
    font-weight: 600;
}
.stButton > button:hover,
.stDownloadButton > button:hover {
    background: #0B2850;
    color: white;
}
[data-testid="stTabs"] button {
    color: #0B2850;
    font-weight: 600;
}
hr {
    border-color: #DCE7F4;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# DATA MANAGEMENT
# ============================================================

COLUMNS = [
    "Year",
    "Month",
    "Buying Price (KES/kg)",
    "Selling Price (KES/kg)",
    "Total Kgs",
    "Expenses (KES)",
    "Net Profit Target (KES)"
]

# Original figures from the supplied 2026 report.
INITIAL_DATA = pd.DataFrame([
    {
        "Year": 2026,
        "Month": "September",
        "Buying Price (KES/kg)": 21.00,
        "Selling Price (KES/kg)": 24.00,
        "Total Kgs": 1388.00,
        "Expenses (KES)": 1500.00,
        "Net Profit Target (KES)": 3000.00
    },
    {
        "Year": 2026,
        "Month": "October",
        "Buying Price (KES/kg)": 20.50,
        "Selling Price (KES/kg)": 24.00,
        "Total Kgs": 2536.60,
        "Expenses (KES)": 0.00,
        "Net Profit Target (KES)": 8000.00
    },
    {
        "Year": 2026,
        "Month": "November",
        "Buying Price (KES/kg)": 20.50,
        "Selling Price (KES/kg)": 24.00,
        "Total Kgs": 3360.00,
        "Expenses (KES)": 0.00,
        "Net Profit Target (KES)": 11760.00
    }
])


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)

            for col in COLUMNS:
                if col not in df.columns:
                    df[col] = np.nan

            df = df[COLUMNS].copy()

            for col in COLUMNS:
                if col != "Month":
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            df["Month"] = df["Month"].astype("string")
            df = df.dropna(subset=["Year", "Month"])

            df["Year"] = df["Year"].astype(int)
            df = df[df["Month"].isin(MONTHS)]

            df = df.drop_duplicates(
                subset=["Year", "Month"],
                keep="last"
            )

            return df.reset_index(drop=True)

        except Exception:
            st.error("Unable to read saved business records.")
            return INITIAL_DATA.copy()

    INITIAL_DATA.to_csv(DATA_FILE, index=False)
    return INITIAL_DATA.copy()


def save_data(df):
    df[COLUMNS].to_csv(DATA_FILE, index=False)


def calculate(df):
    df = df.copy()

    df["Buying Cost (KES)"] = (
        df["Buying Price (KES/kg)"] * df["Total Kgs"]
    )

    df["Total Selling Price (KES)"] = (
        df["Selling Price (KES/kg)"] * df["Total Kgs"]
    )

    df["Gross Profit (KES)"] = (
        df["Total Selling Price (KES)"] -
        df["Buying Cost (KES)"]
    )

    df["Net Profit (KES)"] = (
        df["Gross Profit (KES)"] -
        df["Expenses (KES)"].fillna(0)
    )

    df["Net Margin %"] = np.where(
        df["Total Selling Price (KES)"] > 0,
        df["Net Profit (KES)"] /
        df["Total Selling Price (KES)"] * 100,
        0
    )

    df["Profit Spread (KES/kg)"] = (
        df["Selling Price (KES/kg)"] -
        df["Buying Price (KES/kg)"]
    )

    df["Margin vs Target %"] = np.where(
        df["Net Profit Target (KES)"] > 0,
        (
            df["Net Profit (KES)"] -
            df["Net Profit Target (KES)"]
        ) / df["Net Profit Target (KES)"] * 100,
        0
    )

    df["Target Status"] = np.select(
        [
            df["Net Profit (KES)"] >
            df["Net Profit Target (KES)"],

            df["Net Profit (KES)"] ==
            df["Net Profit Target (KES)"],

            df["Net Profit (KES)"] <
            df["Net Profit Target (KES)"]
        ],
        [
            "Target surpassed",
            "Target met",
            "Target not met"
        ],
        default="Not recorded"
    )

    return df


def kes(value):
    return f"KES {value:,.2f}"


# ============================================================
# INITIALIZE DATA AND NAVIGATION
# ============================================================

if "records" not in st.session_state:
    st.session_state.records = load_data()

df = calculate(st.session_state.records)

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("""
    <div style="text-align:center;padding:15px 5px;">
        <div style="font-size:52px;">🍃</div>
        <div style="font-size:21px;font-weight:800;">
            S&L TEA VENTURES
        </div>
        <div style="font-size:10px;color:#C9E0FA;">
            TEA LEAF BUSINESS MANAGEMENT
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("### NAVIGATION")

    page = st.radio(
        "Navigate",
        [
            "🏠 Home",
            "📝 Data Entry",
            "📈 Monthly Performance",
            "📅 Yearly Performance",
            "📋 Monthly Report"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    selected_year = st.selectbox(
        "Financial Year",
        list(range(2026, 2036)),
        index=0
    )

    st.divider()

    st.caption("🍃 S&L Tea Ventures")
    st.caption("Business Intelligence Dashboard")
    st.caption("All amounts in Kenyan Shillings (KES).")


# ============================================================
# YEAR FILTER
# ============================================================

df = calculate(st.session_state.records)

year_df = df[df["Year"] == selected_year].copy()

year_df["Month Number"] = year_df["Month"].map(
    {m: i + 1 for i, m in enumerate(MONTHS)}
)

year_df = year_df.sort_values("Month Number")

recorded = year_df[year_df["Total Kgs"].fillna(0) > 0].copy()

# ============================================================
# YEAR-TO-DATE CALCULATIONS
# ============================================================

total_months = len(recorded)

total_kgs = recorded["Total Kgs"].sum()
buying_cost = recorded["Buying Cost (KES)"].sum()
selling_total = recorded["Total Selling Price (KES)"].sum()
gross_profit = recorded["Gross Profit (KES)"].sum()
expenses = recorded["Expenses (KES)"].fillna(0).sum()
net_profit = recorded["Net Profit (KES)"].sum()

net_margin = (
    net_profit / selling_total * 100
    if selling_total else 0
)

average_buying = (
    buying_cost / total_kgs if total_kgs else 0
)

average_selling = (
    selling_total / total_kgs if total_kgs else 0
)

profit_spread = average_selling - average_buying

average_kgs = (
    total_kgs / total_months if total_months else 0
)

average_profit = (
    net_profit / total_months if total_months else 0
)

total_target = recorded["Net Profit Target (KES)"].sum()

target_difference = net_profit - total_target

target_difference_pct = (
    target_difference / total_target * 100
    if total_target else 0
)

targets_met = (
    recorded["Net Profit (KES)"] ==
    recorded["Net Profit Target (KES)"]
).sum()

targets_surpassed = (
    recorded["Net Profit (KES)"] >
    recorded["Net Profit Target (KES)"]
).sum()

targets_not_met = (
    recorded["Net Profit (KES)"] <
    recorded["Net Profit Target (KES)"]
).sum()

# Months remaining calculated from the latest recorded month.
if total_months:
    latest_month_number = int(
        recorded["Month"].map(
            {m: i + 1 for i, m in enumerate(MONTHS)}
        ).max()
    )
else:
    latest_month_number = 0

months_remaining = 12 - latest_month_number

projected_profit = (
    net_profit + average_profit * months_remaining
)

annual_target = total_target

projected_vs_target = (
    (projected_profit - annual_target) /
    annual_target * 100
    if annual_target else 0
)


# ============================================================
# LATEST MONTH COMPARISON
# ============================================================

latest = None
previous = None

if total_months:
    latest = recorded.sort_values(
        "Month Number"
    ).iloc[-1]

if total_months >= 2:
    previous = recorded.sort_values(
        "Month Number"
    ).iloc[-2]


# ============================================================
# PAGE HEADER
# ============================================================

st.markdown("""
<div class="hero">
    <h1>🍃 S&L TEA VENTURES</h1>
    <p>TEA LEAF BUSINESS PERFORMANCE & FINANCIAL MANAGEMENT DASHBOARD</p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# HOME DASHBOARD
# ============================================================

if page == "🏠 Home":

    st.markdown(
        f"### YEAR-TO-DATE PERFORMANCE OVERVIEW | {selected_year}"
    )

    if months_remaining > 0:
        st.info(
            f"📌 IN PROGRESS – {months_remaining} month(s) remaining. "
            "The final report updates automatically once December is recorded."
        )
    else:
        st.success("Financial year reporting period completed.")

    # ---------------- TOP KPI CARDS ----------------

    k1, k2, k3, k4, k5 = st.columns(5)

    k1.metric("TOTAL KGS SUPPLIED", f"{total_kgs:,.2f} kg")
    k2.metric("TOTAL BUYING COST", kes(buying_cost))
    k3.metric("TOTAL SELLING VALUE", kes(selling_total))
    k4.metric("GROSS PROFIT", kes(gross_profit))
    k5.metric("NET PROFIT", kes(net_profit))

    k1, k2, k3, k4, k5 = st.columns(5)

    k1.metric("MONTHS REPORTED", total_months)
    k2.metric("TOTAL EXPENSES", kes(expenses))
    k3.metric("NET MARGIN", f"{net_margin:.1f}%")
    k4.metric("AVG BUYING PRICE/KG", f"KES {average_buying:.2f}")
    k5.metric("AVG SELLING PRICE/KG", f"KES {average_selling:.2f}")

    # ---------------- SECOND KPI ROW ----------------

    st.markdown(
        '<div class="section-title">BUSINESS PERFORMANCE SUMMARY</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Profit Spread per KG",
        f"KES {profit_spread:.2f}"
    )

    c2.metric(
        "Average KGs per Month",
        f"{average_kgs:,.2f}"
    )

    c3.metric(
        "Average Net Profit / Month",
        kes(average_profit)
    )

    c4.metric(
        "Months Remaining",
        months_remaining
    )

    # ---------------- MONTHLY COMPARISON ----------------

    st.markdown(
        '<div class="section-title">LATEST MONTH VS PREVIOUS MONTH</div>',
        unsafe_allow_html=True
    )

    if latest is not None and previous is not None:

        comparison = []

        metrics = [
            ("Total Kgs", "Total Kgs", "kg"),
            ("Buying Price per Kg", "Buying Price (KES/kg)", "KES"),
            ("Selling Price per Kg", "Selling Price (KES/kg)", "KES"),
            ("Gross Profit", "Gross Profit (KES)", "KES"),
            ("Net Profit", "Net Profit (KES)", "KES")
        ]

        for label, col, unit in metrics:

            current = float(latest[col])
            old = float(previous[col])

            change = current - old

            change_pct = (
                change / abs(old) * 100
                if old != 0 else 0
            )

            comparison.append({
                "Metric": label,
                str(latest["Month"]): current,
                str(previous["Month"]): old,
                "Change": change,
                "Change %": change_pct
            })

        comparison_df = pd.DataFrame(comparison)

        st.dataframe(
            comparison_df.style.format({
                str(latest["Month"]): "{:,.2f}",
                str(previous["Month"]): "{:,.2f}",
                "Change": "{:+,.2f}",
                "Change %": "{:+.1f}%"
            }),
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("Two recorded months are required for comparison.")

    # ---------------- TARGET PERFORMANCE ----------------

    st.markdown(
        '<div class="section-title">TARGET PERFORMANCE</div>',
        unsafe_allow_html=True
    )

    a, b, c, d = st.columns(4)

    a.metric("Months With Targets", total_months)
    b.metric("Targets Met", int(targets_met))
    c.metric("Targets Surpassed", int(targets_surpassed))
    d.metric("Targets Not Met", int(targets_not_met))

    c1, c2 = st.columns(2)

    with c1:
        st.metric(
            "Total Monthly Targets",
            kes(total_target)
        )

    with c2:
        st.metric(
            "Profit Above / Below Target",
            kes(target_difference),
            delta=f"{target_difference_pct:+.1f}%"
        )

    if total_target > 0:

        if target_difference >= 0:
            st.success(
                f"Target surpassed by {target_difference_pct:.1f}%"
            )
        else:
            st.warning(
                f"Target shortfall of {abs(target_difference_pct):.1f}%"
            )

    # ---------------- HIGHLIGHTS ----------------

    st.markdown(
        '<div class="section-title">BUSINESS HIGHLIGHTS</div>',
        unsafe_allow_html=True
    )

    if not recorded.empty:

        best_profit = recorded.loc[
            recorded["Net Profit (KES)"].idxmax()
        ]

        lowest_profit = recorded.loc[
            recorded["Net Profit (KES)"].idxmin()
        ]

        highest_kg = recorded.loc[
            recorded["Total Kgs"].idxmax()
        ]

        highest_margin = recorded.loc[
            recorded["Net Margin %"].idxmax()
        ]

        h1, h2 = st.columns(2)

        with h1:
            st.markdown("**Best Month – Net Profit**")
            st.success(
                f"{best_profit['Month']} – "
                f"{kes(best_profit['Net Profit (KES)'])}"
            )

            st.markdown("**Lowest Month – Net Profit**")
            st.info(
                f"{lowest_profit['Month']} – "
                f"{kes(lowest_profit['Net Profit (KES)'])}"
            )

        with h2:
            st.markdown("**Highest KGs Supplied**")
            st.success(
                f"{highest_kg['Month']} – "
                f"{highest_kg['Total Kgs']:,.2f} kg"
            )

            st.markdown("**Highest Net Margin**")
            st.info(
                f"{highest_margin['Month']} – "
                f"{highest_margin['Net Margin %']:.1f}%"
            )

    # ---------------- YEAR-END OUTLOOK ----------------

    st.markdown(
        '<div class="section-title">OUTLOOK TO YEAR-END</div>',
        unsafe_allow_html=True
    )

    o1, o2, o3 = st.columns(3)

    o1.metric(
        "Projected Year-End Net Profit",
        kes(projected_profit)
    )

    o2.metric(
        "Annual Target – Recorded Months",
        kes(annual_target)
    )

    o3.metric(
        "Projected vs Target",
        f"{projected_vs_target:+.1f}%"
    )

    st.caption(
        "Projection method: Actual profit to date + average monthly "
        "net profit × months remaining. Indicative estimate only."
    )

    # ---------------- ONE-PAGE VISUAL GRAPHS ----------------

    st.markdown(
        '<div class="section-title">BUSINESS PERFORMANCE GRAPHS</div>',
        unsafe_allow_html=True
    )

    if not recorded.empty:

        g1, g2 = st.columns(2)

        with g1:

            fig = px.bar(
                recorded,
                x="Month",
                y="Total Kgs",
                color="Total Kgs",
                text="Total Kgs",
                color_continuous_scale=["#B9D8F5", BLUE]
            )

            fig.update_traces(
                texttemplate="%{text:,.0f}",
                textposition="outside"
            )

            fig.update_layout(
                title="Monthly Tea Leaf Supply",
                template="plotly_white",
                height=320,
                coloraxis_showscale=False,
                xaxis_title="",
                yaxis_title="Kilograms",
                margin=dict(t=50, b=20)
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with g2:

            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=recorded["Month"],
                y=recorded["Net Profit (KES)"],
                name="Net Profit",
                marker_color=BLUE
            ))

            fig.add_trace(go.Scatter(
                x=recorded["Month"],
                y=recorded["Net Profit Target (KES)"],
                name="Profit Target",
                mode="lines+markers",
                line=dict(color=ORANGE, width=3, dash="dash")
            ))

            fig.update_layout(
                title="Net Profit vs Monthly Target",
                template="plotly_white",
                height=320,
                xaxis_title="",
                yaxis_title="KES",
                margin=dict(t=50, b=20)
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        g3, g4 = st.columns(2)

        with g3:

            fig = px.pie(
                names=["Buying Cost", "Expenses", "Net Profit"],
                values=[
                    buying_cost,
                    expenses,
                    max(net_profit, 0)
                ],
                hole=0.55,
                color_discrete_sequence=[
                    BLUE,
                    ORANGE,
                    GREEN
                ]
            )

            fig.update_layout(
                title="Distribution of Selling Value",
                template="plotly_white",
                height=330
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with g4:

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=recorded["Month"],
                y=recorded["Buying Price (KES/kg)"],
                mode="lines+markers",
                name="Buying Price",
                line=dict(color=BLUE, width=3)
            ))

            fig.add_trace(go.Scatter(
                x=recorded["Month"],
                y=recorded["Selling Price (KES/kg)"],
                mode="lines+markers",
                name="Selling Price",
                line=dict(color=GREEN, width=3)
            ))

            fig.update_layout(
                title="Buying Price vs Selling Price per KG",
                template="plotly_white",
                height=330,
                yaxis_title="KES per kg"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    # ---------------- AUTO COMMENTARY ----------------

    st.markdown(
        '<div class="section-title">AUTOMATIC BUSINESS COMMENTARY</div>',
        unsafe_allow_html=True
    )

    if total_months:

        latest_name = latest["Month"]

        st.write(
            f"As at the end of {latest_name} {selected_year}, "
            f"{total_months} month(s) have been recorded, with "
            f"{total_kgs:,.2f} kg supplied. Total selling value is "
            f"{kes(selling_total)}, against buying costs of "
            f"{kes(buying_cost)}."
        )

        st.write(
            f"Gross profit is {kes(gross_profit)}. After expenses "
            f"of {kes(expenses)}, net profit is {kes(net_profit)}, "
            f"representing a net margin of {net_margin:.1f}%."
        )

        st.write(
            f"The business has met or surpassed {int(targets_met + targets_surpassed)} "
            f"of {total_months} monthly profit targets."
        )

        st.write(
            f"The indicative projected year-end net profit is "
            f"{kes(projected_profit)}."
        )

    else:
        st.info("Enter monthly records to generate business commentary.")


# ============================================================
# DATA ENTRY PAGE
# ============================================================

elif page == "📝 Data Entry":

    st.markdown("## 📝 Monthly Tea Leaf Data Entry")

    st.write(
        "Record your monthly buying price, selling price, "
        "total kilograms, expenses and monthly profit target."
    )

    with st.form("tea_entry_form", clear_on_submit=True):

        col1, col2 = st.columns(2)

        with col1:

            entry_year = st.selectbox(
                "Financial Year",
                list(range(2026, 2036))
            )

            entry_month = st.selectbox(
                "Month",
                MONTHS
            )

            buying_price = st.number_input(
                "Buying Price per KG (KES)",
                min_value=0.0,
                value=20.50,
                step=0.50
            )

            selling_price = st.number_input(
                "Selling Price per KG (KES)",
                min_value=0.0,
                value=24.00,
                step=0.50
            )

        with col2:

            total_weight = st.number_input(
                "Total KGs Supplied",
                min_value=0.0,
                value=0.0,
                step=10.0
            )

            monthly_expenses = st.number_input(
                "Total Monthly Expenses (KES)",
                min_value=0.0,
                value=0.0,
                step=100.0
            )

            monthly_target = st.number_input(
                "Monthly Net Profit Target (KES)",
                min_value=0.0,
                value=5000.0,
                step=500.0
            )

        submitted = st.form_submit_button(
            "💾 SAVE MONTHLY RECORD",
            use_container_width=True
        )

        if submitted:

            if buying_price <= 0 or selling_price <= 0 or total_weight <= 0:
                st.error(
                    "Please enter positive buying price, selling price "
                    "and total kilograms."
                )

            elif selling_price < buying_price:
                st.warning(
                    "Warning: Your selling price is below your buying price."
                )

            else:

                new_record = {
                    "Year": entry_year,
                    "Month": entry_month,
                    "Buying Price (KES/kg)": buying_price,
                    "Selling Price (KES/kg)": selling_price,
                    "Total Kgs": total_weight,
                    "Expenses (KES)": monthly_expenses,
                    "Net Profit Target (KES)": monthly_target
                }

                current = st.session_state.records

                current = current[
                    ~(
                        (current["Year"] == entry_year) &
                        (current["Month"] == entry_month)
                    )
                ]

                current = pd.concat(
                    [current, pd.DataFrame([new_record])],
                    ignore_index=True
                )

                st.session_state.records = current

                save_data(current)

                st.success(
                    f"Successfully saved {entry_month} {entry_year}!"
                )

                st.rerun()

    st.divider()

    st.markdown("### Previously Recorded Months")

    if not df.empty:

        st.dataframe(
            df.sort_values(
                ["Year", "Month"],
                ascending=[False, True]
            ),
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# MONTHLY PERFORMANCE PAGE
# ============================================================

elif page == "📈 Monthly Performance":

    st.markdown(
        f"## 📈 Monthly Performance – {selected_year}"
    )

    if recorded.empty:

        st.info("No monthly records available for this year.")

    else:

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total KGs", f"{total_kgs:,.2f}")
        col2.metric("Gross Profit", kes(gross_profit))
        col3.metric("Net Profit", kes(net_profit))
        col4.metric("Net Margin", f"{net_margin:.1f}%")

        c1, c2 = st.columns(2)

        with c1:

            fig = px.bar(
                recorded,
                x="Month",
                y="Net Profit (KES)",
                color="Net Profit (KES)",
                text="Net Profit (KES)",
                color_continuous_scale=["#B9D8F5", BLUE]
            )

            fig.update_layout(
                title="Monthly Net Profit",
                template="plotly_white",
                coloraxis_showscale=False,
                height=350
            )

            st.plotly_chart(fig, use_container_width=True)

        with c2:

            fig = go.Figure()

            fig.add_bar(
                x=recorded["Month"],
                y=recorded["Net Profit (KES)"],
                name="Actual Net Profit",
                marker_color=BLUE
            )

            fig.add_scatter(
                x=recorded["Month"],
                y=recorded["Net Profit Target (KES)"],
                name="Monthly Target",
                mode="lines+markers",
                line=dict(color=ORANGE, dash="dash", width=3)
            )

            fig.update_layout(
                title="Actual Profit vs Target",
                template="plotly_white",
                height=350
            )

            st.plotly_chart(fig, use_container_width=True)

        c1, c2 = st.columns(2)

        with c1:

            fig = px.bar(
                recorded,
                x="Month",
                y=["Buying Cost (KES)", "Total Selling Price (KES)"],
                barmode="group",
                title="Buying Cost vs Selling Value",
                color_discrete_sequence=[BLUE, GREEN]
            )

            fig.update_layout(
                template="plotly_white",
                height=350
            )

            st.plotly_chart(fig, use_container_width=True)

        with c2:

            fig = px.line(
                recorded,
                x="Month",
                y="Total Kgs",
                markers=True,
                title="Monthly Supply Trend",
                color_discrete_sequence=[BLUE]
            )

            fig.update_layout(
                template="plotly_white",
                height=350
            )

            st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Detailed Monthly Performance")

        st.dataframe(
            recorded.drop(columns=["Month Number"]),
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# YEARLY PERFORMANCE PAGE
# ============================================================

elif page == "📅 Yearly Performance":

    st.markdown("## 📅 Yearly Business Performance")

    yearly_records = calculate(st.session_state.records)

    yearly_summary = []

    for yr in range(2026, 2036):

        temp = yearly_records[
            yearly_records["Year"] == yr
        ]

        yearly_summary.append({

            "Year": yr,

            "Months Recorded": len(
                temp[temp["Total Kgs"] > 0]
            ),

            "Total KGs": temp["Total Kgs"].sum(),

            "Buying Cost (KES)": temp["Buying Cost (KES)"].sum(),

            "Selling Value (KES)": temp[
                "Total Selling Price (KES)"
            ].sum(),

            "Expenses (KES)": temp["Expenses (KES)"].sum(),

            "Gross Profit (KES)": temp[
                "Gross Profit (KES)"
            ].sum(),

            "Net Profit (KES)": temp[
                "Net Profit (KES)"
            ].sum()
        })

    yearly_df = pd.DataFrame(yearly_summary)

    st.dataframe(
        yearly_df.style.format({
            "Total KGs": "{:,.2f}",
            "Buying Cost (KES)": "{:,.2f}",
            "Selling Value (KES)": "{:,.2f}",
            "Expenses (KES)": "{:,.2f}",
            "Gross Profit (KES)": "{:,.2f}",
            "Net Profit (KES)": "{:,.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )

    populated = yearly_df[
        yearly_df["Months Recorded"] > 0
    ]

    if not populated.empty:

        fig = px.bar(
            populated,
            x="Year",
            y="Net Profit (KES)",
            color="Year",
            text="Net Profit (KES)",
            title="Annual Net Profit Comparison",
            color_discrete_sequence=px.colors.sequential.Blues
        )

        fig.update_layout(
            template="plotly_white",
            showlegend=False,
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

        fig = px.bar(
            populated,
            x="Year",
            y=["Buying Cost (KES)", "Selling Value (KES)"],
            barmode="group",
            title="Annual Buying Cost vs Selling Value",
            color_discrete_sequence=[BLUE, GREEN]
        )

        fig.update_layout(
            template="plotly_white",
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)


# ============================================================
# MONTHLY REPORT PAGE
# ============================================================

elif page == "📋 Monthly Report":

    st.markdown(
        f"## 📋 Monthly Financial Report – {selected_year}"
    )

    report_rows = []

    for month in MONTHS:

        temp = recorded[
            recorded["Month"] == month
        ]

        if not temp.empty:

            row = temp.iloc[0]

            report_rows.append({

                "Month": month,

                "Total Kgs": row["Total Kgs"],

                "Buying Cost (KES)": row["Buying Cost (KES)"],

                "Total Selling Price (KES)": row[
                    "Total Selling Price (KES)"
                ],

                "Gross Profit (KES)": row["Gross Profit (KES)"],

                "Expenses (KES)": row["Expenses (KES)"],

                "Net Profit (KES)": row["Net Profit (KES)"],

                "Net Margin %": row["Net Margin %"],

                "Net Profit Target (KES)": row[
                    "Net Profit Target (KES)"
                ],

                "Margin vs Target %": row["Margin vs Target %"],

                "Target Status": row["Target Status"]
            })

        else:

            report_rows.append({

                "Month": month,
                "Total Kgs": 0,
                "Buying Cost (KES)": np.nan,
                "Total Selling Price (KES)": np.nan,
                "Gross Profit (KES)": np.nan,
                "Expenses (KES)": np.nan,
                "Net Profit (KES)": np.nan,
                "Net Margin %": np.nan,
                "Net Profit Target (KES)": np.nan,
                "Margin vs Target %": np.nan,
                "Target Status": "Not recorded"
            })

    report = pd.DataFrame(report_rows)

    st.dataframe(
        report.style.format({
            "Total Kgs": "{:,.2f}",
            "Buying Cost (KES)": "{:,.2f}",
            "Total Selling Price (KES)": "{:,.2f}",
            "Gross Profit (KES)": "{:,.2f}",
            "Expenses (KES)": "{:,.2f}",
            "Net Profit (KES)": "{:,.2f}",
            "Net Margin %": "{:.1f}%",
            "Net Profit Target (KES)": "{:,.2f}",
            "Margin vs Target %": "{:+.1f}%"
        }, na_rep="-"),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("### YEAR TOTAL")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total KGs", f"{total_kgs:,.2f}")
    c2.metric("Buying Cost", kes(buying_cost))
    c3.metric("Selling Value", kes(selling_total))
    c4.metric("Net Profit", kes(net_profit))

    st.markdown("### Automatic Report Commentary")

    if total_months:

        st.write(
            f"During {selected_year}, S&L Tea Ventures has recorded "
            f"{total_months} month(s), supplying {total_kgs:,.2f} kg "
            f"of tea leaf."
        )

        st.write(
            f"Total buying costs stand at {kes(buying_cost)}, "
            f"while total selling value is {kes(selling_total)}."
        )

        st.write(
            f"After deducting expenses of {kes(expenses)}, "
            f"the business has generated net profit of "
            f"{kes(net_profit)}, with a net margin of "
            f"{net_margin:.1f}%."
        )

        st.write(
            f"Average monthly net profit is {kes(average_profit)}. "
            f"The projected year-end net profit is "
            f"{kes(projected_profit)}."
        )

    csv = report.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ DOWNLOAD MONTHLY REPORT",
        data=csv,
        file_name=f"SL_Tea_Ventures_Report_{selected_year}.csv",
        mime="text/csv"
    )

    st.divider()

    st.markdown("### Download Complete Business Records")

    full_csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ DOWNLOAD FULL BUSINESS LEDGER",
        data=full_csv,
        file_name="SL_Tea_Ventures_Full_Ledger.csv",
        mime="text/csv"
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<hr>
<div style="text-align:center;color:#8091A6;font-size:11px;">
    🍃 <b>S&L TEA VENTURES</b><br>
    Tea Leaf Business Management & Performance Dashboard<br>
    All financial values are in Kenyan Shillings (KES).
</div>
""", unsafe_allow_html=True)
