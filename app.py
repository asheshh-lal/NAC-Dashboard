
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Nepal Airlines vs Druk Air Dashboard",
    page_icon="✈️",
    layout="wide",
)

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
IMG_DIR = BASE_DIR / "images"

@st.cache_data
def load_all():
    intl = pd.read_csv(DATA_DIR / "nepal_international.csv")
    dom = pd.read_csv(DATA_DIR / "nepal_domestic.csv")
    analysis = pd.read_csv(DATA_DIR / "nepal_analysis.csv")
    delay_int = pd.read_csv(DATA_DIR / "international_delay_reasons.csv")
    delay_dom = pd.read_csv(DATA_DIR / "domestic_delay_reasons.csv")
    cancel_dom = pd.read_csv(DATA_DIR / "domestic_cancellation_reasons.csv")
    market_int = pd.read_csv(DATA_DIR / "international_market_share.csv")
    market_dom = pd.read_csv(DATA_DIR / "domestic_market_share.csv")
    route_share = pd.read_csv(DATA_DIR / "international_route_share.csv")
    with open(DATA_DIR / "nepal_financials.json", "r") as f:
        nepal_fin = json.load(f)
    with open(DATA_DIR / "drukair_summary.json", "r") as f:
        druk = json.load(f)
    return {
        "intl": intl,
        "dom": dom,
        "analysis": analysis,
        "delay_int": delay_int,
        "delay_dom": delay_dom,
        "cancel_dom": cancel_dom,
        "market_int": market_int,
        "market_dom": market_dom,
        "route_share": route_share,
        "nepal_fin": nepal_fin,
        "druk": druk,
    }

def fmt_int(x):
    return f"{int(round(x)):,}"

def fmt_pct(x):
    return f"{x:.1%}"

def fmt_money(x, symbol="NPR"):
    sign = "-" if x < 0 else ""
    x = abs(float(x))
    if x >= 1_000_000_000:
        return f"{sign}{symbol} {x/1_000_000_000:.2f}B"
    if x >= 1_000_000:
        return f"{sign}{symbol} {x/1_000_000:.2f}M"
    return f"{sign}{symbol} {x:,.0f}"

def card(title, value, sub=None):
    extra = ""
    if sub:
        extra = f"<div style='font-size:14px;color:#d1d5db;margin-top:8px;'>{sub}</div>"

    html = f"""
    <div style='
        padding:20px;
        border-radius:20px;
        background:#1f2937;
        color:#ffffff;
        box-shadow:0 4px 14px rgba(0,0,0,0.35);
        min-height:140px;
    '>
        <div style='font-size:16px;color:#9ca3af;margin-bottom:10px;'>
            {title}
        </div>
        <div style='font-size:34px;font-weight:700;color:#ffffff;line-height:1.2;'>
            {value}
        </div>
        {extra}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

data = load_all()
intl = data["intl"]
dom = data["dom"]
analysis = data["analysis"]
nepal_fin = data["nepal_fin"]
druk = data["druk"]

st.title("Nepal Airlines vs Druk Air Dashboard")
st.caption("Simple comparison dashboard built from Nepal Airlines FY 2079/80 reports and Drukair Annual Report 2023.")

with st.sidebar:
    st.header("View controls")
    selected_months = st.multiselect("Nepal months", intl["Month"].tolist(), default=intl["Month"].tolist())
    show_explanations = st.toggle("Show simple explanations", True)
    show_tables = st.toggle("Show data tables", False)
    st.markdown("---")
    st.markdown("**Audience:** Class 10 level understandable")
    st.markdown("**Use case:** Minister-style briefing")

intl_f = intl[intl["Month"].isin(selected_months)].copy()
dom_f = dom[dom["Month"].isin(selected_months)].copy()

hero1, hero2 = st.columns(2)
with hero1:
    st.image(str(IMG_DIR / "nepal_airlines_plane.png"), caption="Nepal Airlines", use_container_width=True)
with hero2:
    st.image(str(IMG_DIR / "drukair_plane.png"), caption="Druk Air", use_container_width=True)

tabs = st.tabs([
    "Overview",
    "Nepal Airlines Operations",
    "Nepal Airlines Financials",
    "Druk Air",
    "Comparison",
    "Key Findings",
])

with tabs[0]:
    st.subheader("Big picture")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        card("Nepal Intl Passengers", fmt_int(intl_f["Passengers"].sum()), "International only")
    with c2:
        card("Nepal Domestic Passengers", fmt_int(dom_f["Passengers"].sum()), "Domestic only")
    with c3:
        card("Drukair Passengers", fmt_int(druk["passengers"]), "2023 total")
    with c4:
        card("Drukair Flights", fmt_int(druk["flights_total"]), "2023 total")

    c5, c6, c7, c8 = st.columns(4)
    with c5:
        card("Nepal Intl Avg Seat Factor", fmt_pct(intl_f["SeatFactor"].mean()))
    with c6:
        card("Nepal Domestic Avg Seat Factor", fmt_pct(dom_f["SeatFactor"].mean()))
    with c7:
        card("Drukair Load Factor", fmt_pct(druk["load_factor"]))
    with c8:
        card("Nepal Profit After Tax", fmt_money(nepal_fin["profit_after_tax"], "NPR"), "FY 2079/80")

    compare_df = pd.DataFrame({
        "Airline": ["Nepal Airlines (Intl)", "Nepal Airlines (Domestic)", "Druk Air"],
        "Passengers": [intl_f["Passengers"].sum(), dom_f["Passengers"].sum(), druk["passengers"]],
        "Flights": [intl_f["Flights"].sum(), dom_f["Flights"].sum(), druk["flights_total"]],
    })
    left, right = st.columns(2)
    with left:
        fig = px.bar(compare_df, x="Airline", y="Passengers", text_auto=True, title="Passenger comparison")
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)
    with right:
        fig = px.bar(compare_df, x="Airline", y="Flights", text_auto=True, title="Flight comparison")
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)

    if show_explanations:
        st.info(
            "Simple reading: Nepal Airlines is much larger in total passenger volume, especially internationally. "
            "Druk Air is smaller, but its 2023 report shows a strong recovery in flights, passengers, and profitability before tax."
        )

with tabs[1]:
    st.subheader("Nepal Airlines operations")
    op_tab1, op_tab2 = st.tabs(["International", "Domestic"])

    with op_tab1:
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            card("Flights", fmt_int(intl_f["Flights"].sum()))
        with k2:
            card("Passengers", fmt_int(intl_f["Passengers"].sum()))
        with k3:
            card("Freight (kg)", fmt_int(intl_f["FreightKg"].sum()))
        with k4:
            card("Avg Reliability", fmt_pct(intl_f["Reliability"].mean()))

        left, right = st.columns(2)
        with left:
            fig = px.line(intl_f, x="Month", y=["Flights", "Passengers"], markers=True, title="International traffic trend")
            fig.update_layout(height=420)
            st.plotly_chart(fig, use_container_width=True)
        with right:
            fig = px.line(intl_f, x="Month", y=["SeatFactor", "LoadFactor", "Punctuality", "Reliability"], markers=True, title="International service quality")
            fig.update_yaxes(tickformat=".0%")
            fig.update_layout(height=420)
            st.plotly_chart(fig, use_container_width=True)

        left, right = st.columns(2)
        with left:
            fig = px.bar(intl_f, x="Month", y="FreightKg", title="International freight by month")
            fig.update_layout(height=420)
            st.plotly_chart(fig, use_container_width=True)
        with right:
            adu_cols = ["ADU_A320_AKW", "ADU_A320_AKX", "ADU_A330_ALY", "ADU_A330_ALZ"]
            adu_df = intl_f[["Month"] + adu_cols].melt(id_vars="Month", var_name="Aircraft", value_name="Hours")
            fig = px.line(adu_df, x="Month", y="Hours", color="Aircraft", markers=True, title="Aircraft average daily utilization")
            fig.update_layout(height=420)
            st.plotly_chart(fig, use_container_width=True)

        left, right = st.columns(2)
        with left:
            fig = px.pie(data["delay_int"], names="Reason", values="Percentage", title="International delay reasons")
            fig.update_layout(height=420)
            st.plotly_chart(fig, use_container_width=True)
        with right:
            fig = px.line(data["market_int"], x="Year", y="MarketShare", markers=True, title="International market share trend")
            fig.update_yaxes(tickformat=".0%")
            fig.update_layout(height=420)
            st.plotly_chart(fig, use_container_width=True)

        route_df = data["route_share"].melt(id_vars="Route", var_name="Metric", value_name="Share")
        fig = px.bar(route_df, x="Route", y="Share", color="Metric", barmode="group", title="Presence in operating sectors")
        fig.update_yaxes(tickformat=".0%")
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)

    with op_tab2:
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            card("Flights", fmt_int(dom_f["Flights"].sum()))
        with k2:
            card("Passengers", fmt_int(dom_f["Passengers"].sum()))
        with k3:
            card("Freight (kg)", fmt_int(dom_f["FreightKg"].sum()))
        with k4:
            card("Avg Reliability", fmt_pct(dom_f["Reliability"].mean()))

        left, right = st.columns(2)
        with left:
            fig = px.line(dom_f, x="Month", y=["Flights", "Passengers"], markers=True, title="Domestic traffic trend")
            fig.update_layout(height=420)
            st.plotly_chart(fig, use_container_width=True)
        with right:
            fig = px.line(dom_f, x="Month", y=["SeatFactor", "LoadFactor", "Punctuality", "Reliability"], markers=True, title="Domestic service quality")
            fig.update_yaxes(tickformat=".0%")
            fig.update_layout(height=420)
            st.plotly_chart(fig, use_container_width=True)

        left, right = st.columns(2)
        with left:
            fig = px.pie(data["delay_dom"], names="Reason", values="Percentage", title="Domestic delay reasons")
            fig.update_layout(height=420)
            st.plotly_chart(fig, use_container_width=True)
        with right:
            fig = px.pie(data["cancel_dom"], names="Reason", values="Percentage", title="Domestic cancellation reasons")
            fig.update_layout(height=420)
            st.plotly_chart(fig, use_container_width=True)

        left, right = st.columns(2)
        with left:
            fig = px.line(data["market_dom"], x="Year", y="MarketShare", markers=True, title="Domestic market share trend")
            fig.update_yaxes(tickformat=".0%")
            fig.update_layout(height=420)
            st.plotly_chart(fig, use_container_width=True)
        with right:
            adu_cols = ["ADU_ABT", "ADU_ABU"]
            adu_df = dom_f[["Month"] + adu_cols].melt(id_vars="Month", var_name="Aircraft", value_name="Hours")
            fig = px.line(adu_df, x="Month", y="Hours", color="Aircraft", markers=True, title="Domestic aircraft utilization")
            fig.update_layout(height=420)
            st.plotly_chart(fig, use_container_width=True)

    if show_tables:
        st.dataframe(intl_f, use_container_width=True)
        st.dataframe(dom_f, use_container_width=True)

with tabs[2]:
    st.subheader("Nepal Airlines financial snapshot")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        card("Revenue from operations", fmt_money(nepal_fin["revenue_operations"], "NPR"))
    with c2:
        card("Operating profit", fmt_money(nepal_fin["operating_profit"], "NPR"))
    with c3:
        card("Profit after tax", fmt_money(nepal_fin["profit_after_tax"], "NPR"))
    with c4:
        card("Cash at year end", fmt_money(nepal_fin["cash_end_year"], "NPR"))

    left, right = st.columns(2)
    with left:
        bal = pd.DataFrame({
            "Metric": ["Total Assets", "Current Liabilities", "Non-current Liabilities", "Equity"],
            "Value": [
                nepal_fin["assets_current"],
                nepal_fin["current_liabilities"],
                nepal_fin["non_current_liabilities"],
                nepal_fin["equity_current"],
            ]
        })
        fig = px.bar(bal, x="Metric", y="Value", title="Balance sheet snapshot")
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)
    with right:
        pat = pd.DataFrame({
            "Year": ["Previous Year", "Current Year"],
            "Profit After Tax": [nepal_fin["profit_after_tax_previous"], nepal_fin["profit_after_tax"]]
        })
        fig = px.bar(pat, x="Year", y="Profit After Tax", text_auto=True, title="Loss improvement year over year")
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)

    if show_explanations:
        st.warning(
            "Simple reading: Nepal Airlines generated positive operating profit, but still finished the year with a net loss after tax. "
            "The balance sheet also shows negative equity, so financial recovery is still incomplete."
        )

with tabs[3]:
    st.subheader("Druk Air 2023 summary")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        card("Flights", fmt_int(druk["flights_total"]))
    with c2:
        card("Passengers", fmt_int(druk["passengers"]))
    with c3:
        card("Cargo (kg)", fmt_int(druk["cargo_kg"]))
    with c4:
        card("Load factor", fmt_pct(druk["load_factor"]))

    c5, c6, c7, c8 = st.columns(4)
    with c5:
        card("Operating revenue", fmt_money(druk["operating_revenue_nu"], "Nu."))
    with c6:
        card("Operating profit", fmt_money(druk["operating_profit_nu"], "Nu."))
    with c7:
        card("Profit before tax", fmt_money(druk["profit_before_tax_nu"], "Nu."))
    with c8:
        card("Profit after tax", fmt_money(druk["profit_after_tax_nu"], "Nu."))

    left, right = st.columns(2)
    with left:
        druk_fin = pd.DataFrame({
            "Metric": ["Total Assets", "Equity", "Non-current Liabilities", "Current Liabilities"],
            "Value": [
                druk["total_assets_nu"],
                druk["equity_nu"],
                druk["non_current_liabilities_nu"],
                druk["current_liabilities_nu"],
            ]
        })
        fig = px.bar(druk_fin, x="Metric", y="Value", title="Druk Air financial position")
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)
    with right:
        op = pd.DataFrame({
            "Metric": ["Operating Revenue", "Operating Expenditure", "Operating Profit", "Finance Cost"],
            "Value": [
                druk["operating_revenue_nu"],
                druk["operating_expenditure_nu"],
                druk["operating_profit_nu"],
                druk["finance_cost_nu"],
            ]
        })
        fig = px.bar(op, x="Metric", y="Value", title="Druk Air income summary")
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)

    if show_explanations:
        st.success(
            "Simple reading: Druk Air is much smaller than Nepal Airlines, but its 2023 report shows strong recovery. "
            "Flights and passengers increased sharply, it earned operating profit, and profit before tax turned positive."
        )

with tabs[4]:
    st.subheader("Nepal vs Druk Air comparison")

    compare_kpi = pd.DataFrame({
        "Airline": ["Nepal Airlines Intl", "Druk Air"],
        "Passengers": [intl["Passengers"].sum(), druk["passengers"]],
        "Flights": [intl["Flights"].sum(), druk["flights_total"]],
        "FreightKg": [intl["FreightKg"].sum(), druk["cargo_kg"]],
    })
    left, right = st.columns(2)
    with left:
        fig = px.bar(compare_kpi.melt(id_vars="Airline", var_name="Metric", value_name="Value"),
                     x="Metric", y="Value", color="Airline", barmode="group",
                     title="Scale comparison")
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)
    with right:
        ratio = pd.DataFrame({
            "Metric": ["Load / Seat Factor", "Market Share", "Net Profitability"],
            "Nepal Airlines": [intl["SeatFactor"].mean(), data["market_int"]["MarketShare"].iloc[-1], nepal_fin["profit_after_tax"] / max(nepal_fin["revenue_operations"], 1)],
            "Druk Air": [druk["load_factor"], druk["market_share_competitive_routes"], druk["profit_after_tax_nu"] / max(druk["operating_revenue_nu"], 1)],
        })
        fig = go.Figure()
        for col in ["Nepal Airlines", "Druk Air"]:
            fig.add_trace(go.Bar(name=col, x=ratio["Metric"], y=ratio[col]))
        fig.update_layout(height=420, barmode="group", title="Efficiency and outcome comparison")
        fig.update_yaxes(tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)

    lessons = pd.DataFrame({
        "Area": ["Scale", "Punctuality", "Weather Risk", "Commercial Recovery", "Balance Sheet"],
        "Nepal Airlines": [
            "Much larger passenger base",
            "Weak punctuality despite strong reliability",
            "Domestic heavily weather-affected",
            "Large international network but market share below 2020 peak",
            "Negative equity and net loss"
        ],
        "Druk Air": [
            "Smaller but more compact operation",
            "Report highlights recovery and utilization focus",
            "Mountain geography remains structural challenge",
            "Strong post-pandemic recovery in flights and revenue",
            "Positive equity and positive profit before tax"
        ]
    })
    st.dataframe(lessons, use_container_width=True, hide_index=True)

with tabs[5]:
    st.subheader("Key findings from Nepal Airlines analysis sheet")
    for _, row in analysis.iterrows():
        with st.expander(row["Finding"]):
            st.markdown(f"**Evidence:** {row['Evidence']}")
            st.markdown(f"**Likely cause:** {row['Likely Cause']}")
            st.markdown(f"**Recommended action:** {row['Recommended Actions']}")

    st.markdown("### Short minister briefing")
    st.markdown(
        """
        1. Nepal Airlines is much larger in passenger volume than Druk Air, especially on international routes.
        2. Nepal Airlines' biggest operational weakness in the report is punctuality, not reliability.
        3. Nepal domestic operations are strongly affected by weather in both delays and cancellations.
        4. Nepal Airlines improved from the previous year, but still shows net loss and negative equity.
        5. Druk Air is smaller, but its 2023 report shows strong recovery in traffic, revenue, and profit before tax.
        6. A practical policy focus for Nepal would be punctuality improvement, weather resilience, and financial restructuring.
        """
    )

st.divider()
st.caption("Run locally with: streamlit run app.py")
