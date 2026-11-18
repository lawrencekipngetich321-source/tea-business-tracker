import os
from pathlib import Path
from datetime import date
import calendar

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Tea Leaf Trading Dashboard", page_icon="🍃", layout="wide")
DATA_FILE = Path(__file__).with_name("tea_data.csv")
MONTHS = list(calendar.month_name)[1:]
YEARS = list(range(2026, 2036))
INPUTS = ["Year", "Month", "Buying Price (KES/kg)", "Total Kgs",
          "Selling Price (KES/kg)", "Expenses Incurred (KES)"]

st.markdown("""
<style>
.stApp{background:#F5F8FC;color:#14243A}
.block-container{padding-top:1.5rem;max-width:1500px}
h1,h2,h3{color:#102F56}
.hero{background:linear-gradient(115deg,#0B2E59,#1769AA,#3988D5);padding:1.4rem 1.6rem;border-radius:16px;color:white;margin-bottom:1rem}
.hero h1{color:white!important;margin:0}.hero p{color:#EAF3FF;margin:.35rem 0 0}
div[data-testid="stMetric"]{background:white;border:1px solid #DCE8F5;border-left:4px solid #287BC1;padding:14px;border-radius:12px;box-shadow:0 3px 12px #1846780d}
[data-testid="stSidebar"]{background:#EAF3FF}
.stButton>button,.stDownloadButton>button{background:#1769AA;color:white;border:0;border-radius:9px;font-weight:600}
.stButton>button:hover,.stDownloadButton>button:hover{background:#0B2E59;color:white}
</style>
""", unsafe_allow_html=True)

def check_password():
    try:
        expected = st.secrets.get("APP_PASSWORD", "")
    except Exception:
        expected = ""
    if not expected:
        return True
    if st.session_state.get("authenticated"):
        return True
    st.markdown('<div class="hero"><h1>🔒 Private Tea Business Login</h1><p>Sign in to continue</p></div>', unsafe_allow_html=True)
    pwd = st.text_input("Admin password", type="password")
    if st.button("Login"):
        if pwd == expected:
            st.session_state.authenticated = True
            st.rerun()
        st.error("Incorrect password.")
    return False

if not check_password():
    st.stop()

def load_data():
    if not DATA_FILE.exists():
        return pd.DataFrame(columns=INPUTS)
    d = pd.read_csv(DATA_FILE)
    for c in INPUTS:
        if c not in d:
            d[c] = np.nan
    d = d[INPUTS].copy()
    d["Year"] = pd.to_numeric(d["Year"], errors="coerce")
    for c in INPUTS[2:]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d["Month"] = d["Month"].astype("string")
    d = d.dropna(subset=["Year", "Month"])
    d["Year"] = d["Year"].astype(int)
    d = d[d["Month"].isin(MONTHS)].drop_duplicates(["Year","Month"], keep="last")
    d["_month"] = d["Month"].map({m:i for i,m in enumerate(MONTHS)})
    return d.sort_values(["Year","_month"]).drop(columns="_month").reset_index(drop=True)

def save_data(d):
    d[INPUTS].to_csv(DATA_FILE, index=False)

def settings():
    defaults = {"expense_per_kg":0.0,"fixed_expenses":0.0,"target_margin":0.12,
                "method":"Exponential Smoothing","alpha":0.5}
    if "business_settings" not in st.session_state:
        st.session_state.business_settings = defaults
    return st.session_state.business_settings

def calculate(d,s):
    x=d.copy()
    x["Buying Cost (KES)"]=x["Buying Price (KES/kg)"]*x["Total Kgs"]
    x["Selling Total (KES)"]=x["Selling Price (KES/kg)"]*x["Total Kgs"]
    estimate=s["fixed_expenses"]+s["expense_per_kg"]*x["Total Kgs"]
    x["Expenses (KES)"]=x["Expenses Incurred (KES)"].where(x["Expenses Incurred (KES)"].notna(),estimate)
    x["Gross Profit (KES)"]=x["Selling Total (KES)"]-x["Buying Cost (KES)"]
    x["Net Profit (KES)"]=x["Gross Profit (KES)"]-x["Expenses (KES)"]
    x["Net Margin %"]=np.where(x["Selling Total (KES)"]>0,x["Net Profit (KES)"]/x["Selling Total (KES)"],np.nan)
    x["Profit per kg (KES)"]=np.where(x["Total Kgs"]>0,x["Net Profit (KES)"]/x["Total Kgs"],np.nan)
    x["Net Profit Target (KES)"]=x["Selling Total (KES)"]*s["target_margin"]
    x["Target Status"]=np.where(x["Net Profit (KES)"]>=x["Net Profit Target (KES)"],"Target met / surpassed","Target not met")
    return x

def forecast(vals,method,alpha):
    v=pd.Series(vals).dropna().astype(float).tolist()
    if not v:return 0.0
    if method=="Latest Month" or len(v)==1:return float(v[-1])
    if method=="Weighted Moving Average":
        v=v[-3:];return float(np.average(v,weights=np.arange(1,len(v)+1)))
    if method=="Linear Trend":
        a,b=np.polyfit(np.arange(len(v)),np.array(v),1)
        return max(0.0,float(b+a*len(v)))
    f=v[0]
    for actual in v[1:]:f=alpha*actual+(1-alpha)*f
    return float(f)

def kes(v): return f"KES {v:,.0f}"

s=settings()
raw=load_data()
d=calculate(raw,s)

st.markdown('<div class="hero"><h1>🍃 Tea Leaf Trading Dashboard</h1><p>Business performance • Monthly reports • 10-year comparison • Buying price projections</p></div>',unsafe_allow_html=True)

with st.sidebar:
    st.header("Dashboard controls")
    years=sorted(set(YEARS+raw["Year"].tolist()))
    selected=st.selectbox("Reporting year",years,index=years.index(2026) if 2026 in years else 0)
    st.divider()
    st.subheader("➕ Add / update monthly figures")
    with st.form("entry",clear_on_submit=False):
        yr=st.selectbox("Year",years,index=years.index(selected))
        mo=st.selectbox("Month",MONTHS,index=date.today().month-1)
        old=raw[(raw.Year==yr)&(raw.Month==mo)]
        old=old.iloc[0] if not old.empty else None
        buy=st.number_input("Buying price (KES/kg)",min_value=0.0,value=float(old["Buying Price (KES/kg)"]) if old is not None and pd.notna(old["Buying Price (KES/kg)"]) else 20.5,step=.5)
        kg=st.number_input("Total kilograms",min_value=0.0,value=float(old["Total Kgs"]) if old is not None and pd.notna(old["Total Kgs"]) else 0.0,step=10.0)
        sell=st.number_input("Selling price (KES/kg)",min_value=0.0,value=float(old["Selling Price (KES/kg)"]) if old is not None and pd.notna(old["Selling Price (KES/kg)"]) else 24.0,step=.5)
        old_exp=float(old["Expenses Incurred (KES)"]) if old is not None and pd.notna(old["Expenses Incurred (KES)"]) else 0.0
        use_est=st.checkbox("Use automatic expense estimate",value=old is None or pd.isna(old["Expenses Incurred (KES)"]))
        exp=st.number_input("Actual expenses (KES)",min_value=0.0,value=old_exp,step=100.0,disabled=use_est)
        submitted=st.form_submit_button("💾 Save / update month",use_container_width=True)
        if submitted:
            if min(buy,kg,sell)<=0:
                st.error("Enter positive buying price, kilograms and selling price.")
            else:
                raw=raw[~((raw.Year==yr)&(raw.Month==mo))]
                row={"Year":yr,"Month":mo,"Buying Price (KES/kg)":buy,"Total Kgs":kg,
                     "Selling Price (KES/kg)":sell,"Expenses Incurred (KES)":np.nan if use_est else exp}
                raw=pd.concat([raw,pd.DataFrame([row])],ignore_index=True)
                save_data(raw);st.success("Month saved.");st.rerun()
    st.divider()
    if st.button("Logout"):
        st.session_state.authenticated=False
        st.rerun()

# Recalculate after entry form reruns
raw=load_data();d=calculate(raw,s)
yd=d[d.Year==selected].copy()
yd["_m"]=yd.Month.map({m:i for i,m in enumerate(MONTHS)})
yd=yd.sort_values("_m")
reported=yd[yd["Total Kgs"].fillna(0)>0]
kg_total=reported["Total Kgs"].sum()
buy_total=reported["Buying Cost (KES)"].sum()
sell_total=reported["Selling Total (KES)"].sum()
expenses=reported["Expenses (KES)"].sum()
gross=reported["Gross Profit (KES)"].sum()
net=reported["Net Profit (KES)"].sum()
margin=net/sell_total if sell_total else 0
avg_buy=buy_total/kg_total if kg_total else 0
avg_sell=sell_total/kg_total if kg_total else 0
met=int((reported["Net Profit (KES)"]>=reported["Net Profit Target (KES)"]).sum())

st.subheader(f"📊 {selected} performance overview")
cols=st.columns(5)
for col,label,value in zip(cols,["Total supplied","Selling total","Buying cost","Net profit","Net margin"],
                           [f"{kg_total:,.1f} kg",kes(sell_total),kes(buy_total),kes(net),f"{margin:.1%}"]):
    col.metric(label,value)
cols=st.columns(5)
for col,label,value in zip(cols,["Gross profit","Expenses","Avg buying / kg","Avg selling / kg","Months target met"],
                           [kes(gross),kes(expenses),f"KES {avg_buy:,.2f}",f"KES {avg_sell:,.2f}",f"{met}/{len(reported)}"]):
    col.metric(label,value)

dash,monthly,yearly,assumptions,ledger=st.tabs(["📈 Dashboard","🗓️ Monthly report","📅 10-year comparison","⚙️ Assumptions","📋 Data ledger"])
with dash:
    if reported.empty: st.info(f"No entries for {selected} yet. Add a month from the sidebar.")
    c1,c2=st.columns(2)
    with c1:
        st.markdown("#### Monthly kilograms supplied")
        fig=px.bar(yd,x="Month",y="Total Kgs",color_discrete_sequence=["#1976D2"],text_auto=".0f")
        fig.update_layout(template="plotly_white",xaxis_title="",yaxis_title="Kilograms")
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        st.markdown("#### Selling total, buying cost and expenses")
        if not reported.empty:
            long=reported.melt(id_vars="Month",value_vars=["Selling Total (KES)","Buying Cost (KES)","Expenses (KES)"],var_name="Type",value_name="KES")
            fig=px.bar(long,x="Month",y="KES",color="Type",barmode="group",color_discrete_sequence=["#1769AA","#62A9E8","#F4A261"])
            fig.update_layout(template="plotly_white",xaxis_title="")
            st.plotly_chart(fig,use_container_width=True)
    c1,c2=st.columns(2)
    with c1:
        st.markdown("#### Net profit by month")
        fig=px.area(yd,x="Month",y="Net Profit (KES)",markers=True,color_discrete_sequence=["#1769AA"])
        fig.update_layout(template="plotly_white",xaxis_title="")
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        st.markdown("#### Actual net margin vs target")
        if not reported.empty:
            fig=go.Figure()
            fig.add_bar(x=reported.Month,y=reported["Net Margin %"],name="Actual",marker_color="#1769AA")
            fig.add_scatter(x=reported.Month,y=[s["target_margin"]]*len(reported),name="Target",mode="lines",line=dict(color="#F4A261",dash="dash",width=3))
            fig.update_layout(template="plotly_white",yaxis_tickformat=".0%",xaxis_title="")
            st.plotly_chart(fig,use_container_width=True)

    st.markdown("#### 🔮 Next-month buying guide")
    history=d[d["Total Kgs"].fillna(0)>0].copy()
    history["_date"]=history.Year*12+history.Month.map({m:i for i,m in enumerate(MONTHS)})
    history=history.sort_values("_date")
    if not history.empty:
        pk=forecast(history["Total Kgs"],s["method"],s["alpha"])
        ps=forecast(history["Selling Price (KES/kg)"],s["method"],s["alpha"])
        pb=forecast(history["Buying Price (KES/kg)"],s["method"],s["alpha"])
        maxbuy=ps*(1-s["target_margin"])-s["expense_per_kg"]-(s["fixed_expenses"]/pk if pk else 0)
        pexp=s["fixed_expenses"]+s["expense_per_kg"]*pk
        pprofit=(ps-maxbuy)*pk-pexp
        a,b,c,e=st.columns(4)
        a.metric("Projected kilograms",f"{pk:,.1f}")
        b.metric("Projected selling price",f"KES {ps:,.2f}/kg")
        c.metric("Buying price trend",f"KES {pb:,.2f}/kg")
        e.metric("Maximum buying price",f"KES {maxbuy:,.2f}/kg")
        st.metric("Projected net profit at target buying price",kes(pprofit))
        st.caption(f"Method: {s['method']} • Target net margin: {s['target_margin']:.1%}. Maximum buying price is an estimate based on the configured expense assumptions.")

with monthly:
    st.markdown(f"#### Monthly report — {selected}")
    cols=["Month","Total Kgs","Buying Price (KES/kg)","Buying Cost (KES)","Selling Price (KES/kg)","Selling Total (KES)","Expenses (KES)","Gross Profit (KES)","Net Profit (KES)","Net Margin %","Profit per kg (KES)","Net Profit Target (KES)","Target Status"]
    if not yd.empty:
        table=yd[cols].copy()
        table["Net Margin %"]=table["Net Margin %"].map(lambda x:f"{x:.1%}" if pd.notna(x) else "—")
        st.dataframe(table,use_container_width=True,hide_index=True)
    if len(reported)>0:
        st.success(f"{met} of {len(reported)} reported months met or exceeded the {s['target_margin']:.0%} net-profit target.")

with yearly:
    st.markdown("#### Ten-year performance comparison")
    rows=[]
    for y in YEARS:
        q=d[(d.Year==y)&(d["Total Kgs"].fillna(0)>0)]
        k=q["Total Kgs"].sum();sales=q["Selling Total (KES)"].sum()
        costs=q["Buying Cost (KES)"].sum();ex=q["Expenses (KES)"].sum()
        npf=q["Net Profit (KES)"].sum()
        rows.append({"Year":y,"Months reported":len(q),"Total Kgs":k,"Buying cost (KES)":costs,
                     "Selling total (KES)":sales,"Expenses (KES)":ex,"Gross profit (KES)":sales-costs,
                     "Net profit (KES)":npf,"Net margin %":npf/sales if sales else np.nan})
    yearly_df=pd.DataFrame(rows)
    st.dataframe(yearly_df.style.format({"Total Kgs":"{:,.1f}","Buying cost (KES)":"{:,.0f}","Selling total (KES)":"{:,.0f}",
        "Expenses (KES)":"{:,.0f}","Gross profit (KES)":"{:,.0f}","Net profit (KES)":"{:,.0f}","Net margin %":"{:.1%}"}),
        use_container_width=True,hide_index=True)
    populated=yearly_df[yearly_df["Months reported"]>0]
    if not populated.empty:
        fig=px.bar(populated,x="Year",y="Net profit (KES)",color_discrete_sequence=["#1769AA"],text_auto=".0f")
        fig.update_layout(template="plotly_white",xaxis_title="")
        st.plotly_chart(fig,use_container_width=True)

with assumptions:
    st.markdown("#### Business assumptions")
    st.caption("Blank monthly expenses use fixed monthly expenses + (expense per kg × kilograms).")
    with st.form("settings"):
        ep=st.number_input("Operating expenses per kg (KES/kg)",min_value=0.0,value=float(s["expense_per_kg"]),step=.5)
        fixed=st.number_input("Fixed monthly expenses (KES)",min_value=0.0,value=float(s["fixed_expenses"]),step=100.0)
        target=st.number_input("Target net profit margin (%)",min_value=0.0,max_value=95.0,value=float(s["target_margin"]*100),step=1.0)
        methods=["Exponential Smoothing","Weighted Moving Average","Linear Trend","Latest Month"]
        method=st.selectbox("Projection method",methods,index=methods.index(s["method"]))
        alpha=st.slider("Smoothing factor α",.1,.9,float(s["alpha"]),.1)
        if st.form_submit_button("Save assumptions"):
            st.session_state.business_settings={"expense_per_kg":ep,"fixed_expenses":fixed,"target_margin":target/100,"method":method,"alpha":alpha}
            st.success("Settings saved for this app session.");st.rerun()
    st.info("Workbook starting assumptions: variable expenses KES 0/kg, fixed expenses KES 0/month, target margin 12%, Exponential Smoothing, α = 0.5.")

with ledger:
    st.markdown("#### Complete trading ledger")
    ledger_df=calculate(raw,s).sort_values(["Year","Month"],ascending=[False,True])
    st.dataframe(ledger_df,use_container_width=True,hide_index=True)
    st.download_button("⬇️ Download full ledger CSV",ledger_df.to_csv(index=False).encode("utf-8"),
                       "tea_leaf_trading_ledger.csv","text/csv")
    uploaded=st.file_uploader("Import records from CSV",type=["csv"])
    if uploaded is not None:
        try:
            incoming=pd.read_csv(uploaded)
            missing=[c for c in INPUTS if c not in incoming.columns]
            if missing: st.error("CSV is missing: "+", ".join(missing))
            elif st.button("Import and replace all records"):
                save_data(incoming[INPUTS]);st.success("CSV imported.");st.rerun()
        except Exception as exc:
            st.error(f"Unable to read CSV: {exc}")

st.caption("Tea Leaf Trading Dashboard • All financial values are in Kenyan shillings (KES).")
