import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Nepal Airlines Dashboard",
    page_icon="✈️",
    layout="wide",
)

BASE_DIR = Path(__file__).parent

@st.cache_data
def load_data():
    international = pd.read_csv(BASE_DIR / "international_operations.csv")
    domestic = pd.read_csv(BASE_DIR / "domestic_operations.csv")
    delay_int = pd.read_csv(BASE_DIR / "international_delay_reasons.csv")
    delay_dom = pd.read_csv(BASE_DIR / "domestic_delay_reasons.csv")
    cancel_dom = pd.read_csv(BASE_DIR / "domestic_cancellation_reasons.csv")
    market_int = pd.read_csv(BASE_DIR / "international_market_share.csv")
    market_dom = pd.read_csv(BASE_DIR / "domestic_market_share.csv")
    route_share = pd.read_csv(BASE_DIR / "international_route_share.csv")
    with open(BASE_DIR / "financial_snapshot.json", "r") as f:
        financial = json.load(f)
    return {
        "international": international,
        "domestic": domestic,
        "delay_int": delay_int,
        "delay_dom": delay_dom,
        "cancel_dom": cancel_dom,
        "market_int": market_int,
        "market_dom": market_dom,
        "route_share": route_share,
        "financial": financial,
    }


def fmt_int(value):
    return f"{int(round(value)):,}"


def fmt_pct(value):
    return f"{value:.1%}"


def fmt_npr(value):
    sign = "-" if value < 0 else ""
    value = abs(value)
    if value >= 1_000_000_000:
        return f"{sign}NPR {value/1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"{sign}NPR {value/1_000_000:.2f}M"
    return f"{sign}NPR {value:,.0f}"


def kpi_card(title, value, help_text=None):
    st.markdown(
        f"""
        <div style='padding:1rem;border:1px solid #e5e7eb;border-radius:16px;background:#ffffff;'>
            <div style='font-size:0.9rem;color:#6b7280;'>{title}</div>
            <div style='font-size:1.8rem;font-weight:700;margin-top:0.2rem;'>{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
        help=help_text,
    )


def metric_definitions():
    with st.expander("Metric definitions"):
        st.markdown(
            """
            - **ASKM**: Available Seat Kilometer
            - **RPKM**: Revenue Passenger Kilometer
            - **ATKM**: Available Ton Kilometer
            - **RTKM**: Revenue Ton Kilometer
            - **Seat Factor**: seat occupancy efficiency
            - **Load Factor**: combined passenger/cargo utilization indicator used in the report
            - **ADU**: Average Daily Utilization of aircraft
            """
        )


data = load_data()
intl = data["international"]
dom = data["domestic"]
financial = data["financial"]

st.title("Nepal Airlines Operations & Financial Dashboard")
st.caption("Built from FY 2079/80 annual report and financial statement extracts.")

with st.sidebar:
    st.header("Controls")
    sector = st.selectbox("Sector", ["International", "Domestic", "Both"])
    month_order = list(intl["Month"]) if sector != "Domestic" else list(dom["Month"])
    selected_months = st.multiselect("Months", month_order, default=month_order)
    show_financials = st.toggle("Show financial snapshot", value=True)
    show_route_panel = st.toggle("Show route/market share panels", value=True)

metric_definitions()

if sector == "International":
    ops = intl[intl["Month"].isin(selected_months)].copy()
elif sector == "Domestic":
    ops = dom[dom["Month"].isin(selected_months)].copy()
else:
    intl2 = intl[intl["Month"].isin(selected_months)].copy()
    intl2["Sector"] = "International"
    dom2 = dom[dom["Month"].isin([m for m in dom["Month"] if m in selected_months or len(selected_months) == len(month_order)])].copy()
    dom2["Sector"] = "Domestic"
    ops = pd.concat([intl2, dom2], ignore_index=True)

st.subheader("Executive summary")
if sector == "Both":
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi_card("Total Flights", fmt_int(ops["Flights"].sum()))
    with col2:
        kpi_card("Total Passengers", fmt_int(ops["Passengers"].sum()))
    with col3:
        kpi_card("Average Seat Factor", fmt_pct(ops["SeatFactor"].mean()))
    with col4:
        kpi_card("Average Reliability", fmt_pct(ops["Reliability"].mean()))
else:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi_card("Total Flights", fmt_int(ops["Flights"].sum()))
    with col2:
        kpi_card("Total Passengers", fmt_int(ops["Passengers"].sum()))
    with col3:
        kpi_card("Total Freight (kg)", fmt_int(ops["FreightKg"].sum()))
    with col4:
        kpi_card("Average Seat Factor", fmt_pct(ops["SeatFactor"].mean()))

st.markdown("### Traffic trends")
left, right = st.columns((1.3, 1))
with left:
    if sector == "Both":
        fig = px.line(
            ops,
            x="Month",
            y="Passengers",
            color="Sector",
            markers=True,
            title="Passengers by month",
        )
    else:
        fig = px.line(ops, x="Month", y=["Flights", "Passengers"], markers=True, title=f"{sector} traffic")
    fig.update_layout(height=420)
    st.plotly_chart(fig, use_container_width=True)
with right:
    if sector == "Both":
        grouped = ops.groupby("Sector", as_index=False)[["Passengers", "Flights", "FreightKg"]].sum()
        fig = px.bar(grouped.melt(id_vars="Sector", var_name="Metric", value_name="Value"), x="Metric", y="Value", color="Sector", barmode="group", title="Sector comparison")
    else:
        fig = px.bar(ops, x="Month", y="FreightKg", title=f"{sector} freight by month")
    fig.update_layout(height=420)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("### Efficiency and service quality")
col_a, col_b = st.columns(2)
with col_a:
    if sector == "Both":
        eff = ops.groupby("Sector", as_index=False)[["SeatFactor", "LoadFactor", "Punctuality", "Reliability"]].mean()
        fig = go.Figure()
        for metric in ["SeatFactor", "LoadFactor", "Punctuality", "Reliability"]:
            fig.add_trace(go.Bar(name=metric, x=eff["Sector"], y=eff[metric]))
        fig.update_layout(barmode="group", title="Average service KPIs", height=420, yaxis_tickformat=".0%")
    else:
        fig = px.line(
            ops,
            x="Month",
            y=["SeatFactor", "LoadFactor", "Punctuality", "Reliability"],
            markers=True,
            title=f"{sector} KPI trend",
        )
        fig.update_layout(height=420, yaxis_tickformat=".0%")
    st.plotly_chart(fig, use_container_width=True)
with col_b:
    if sector == "International":
        adu_cols = ["ADU_A320_AKW", "ADU_A320_AKX", "ADU_A330_ALY", "ADU_A330_ALZ"]
    elif sector == "Domestic":
        adu_cols = ["ADU_ABT", "ADU_ABU"]
    else:
        adu_cols = []

    if adu_cols:
        adu_df = ops[["Month"] + adu_cols].melt(id_vars="Month", var_name="Aircraft", value_name="ADU")
        fig = px.line(adu_df, x="Month", y="ADU", color="Aircraft", markers=True, title="Aircraft utilization")
    else:
        util = pd.DataFrame(
            {
                "Sector": ["International", "Domestic"],
                "Avg ASKM": [intl["ASKM"].mean(), dom["ASKM"].mean()],
                "Avg RPKM": [intl["RPKM"].mean(), dom["RPKM"].mean()],
            }
        )
        fig = px.bar(util.melt(id_vars="Sector", var_name="Metric", value_name="Value"), x="Sector", y="Value", color="Metric", barmode="group", title="Capacity vs realized traffic")
    fig.update_layout(height=420)
    st.plotly_chart(fig, use_container_width=True)

if show_route_panel:
    st.markdown("### Delays and market share")
    col_c, col_d = st.columns(2)
    with col_c:
        if sector == "International":
            fig = px.pie(data["delay_int"], names="Reason", values="Percentage", title="International delay reasons")
        elif sector == "Domestic":
            tab1, tab2 = st.tabs(["Delay reasons", "Cancellation reasons"])
            with tab1:
                fig1 = px.pie(data["delay_dom"], names="Reason", values="Percentage", title="Domestic delay reasons")
                st.plotly_chart(fig1, use_container_width=True)
            with tab2:
                fig2 = px.pie(data["cancel_dom"], names="Reason", values="Percentage", title="Domestic cancellation reasons")
                st.plotly_chart(fig2, use_container_width=True)
            fig = None
        else:
            delays = pd.DataFrame({
                "Category": ["Intl: Immigration", "Intl: SUBS", "Intl: Marketing/Customer", "Dom: Weather/NOTAM", "Dom: ATC"],
                "Share": [0.33, 0.30, 0.14, 0.54, 0.35]
            })
            fig = px.bar(delays, x="Category", y="Share", title="Largest delay drivers", text_auto=".0%")
            fig.update_yaxes(tickformat=".0%")
        if fig is not None:
            fig.update_layout(height=420)
            st.plotly_chart(fig, use_container_width=True)
    with col_d:
        if sector == "International":
            fig = px.line(data["market_int"], x="Year", y="MarketShare", markers=True, title="International market share")
            fig.update_yaxes(tickformat=".0%")
            st.plotly_chart(fig, use_container_width=True)
            route_fig = px.bar(data["route_share"].melt(id_vars="Route", var_name="Metric", value_name="Share"), x="Route", y="Share", color="Metric", barmode="group", title="Presence in operating sectors")
            route_fig.update_yaxes(tickformat=".0%")
            st.plotly_chart(route_fig, use_container_width=True)
        elif sector == "Domestic":
            fig = px.line(data["market_dom"], x="Year", y="MarketShare", markers=True, title="Domestic market share")
            fig.update_yaxes(tickformat=".0%")
            fig.update_layout(height=420)
            st.plotly_chart(fig, use_container_width=True)
        else:
            market_compare = pd.DataFrame({
                "Sector": ["International", "Domestic"],
                "2022 Market Share": [data["market_int"].iloc[-1]["MarketShare"], data["market_dom"].iloc[-1]["MarketShare"]],
            })
            fig = px.bar(market_compare, x="Sector", y="2022 Market Share", text_auto=".1%", title="2022 market share comparison")
            fig.update_yaxes(tickformat=".0%")
            fig.update_layout(height=420)
            st.plotly_chart(fig, use_container_width=True)

if show_financials:
    st.markdown("### Financial snapshot")
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        kpi_card("Revenue from operations", fmt_npr(financial["revenue_operations"]))
    with f2:
        kpi_card("Operating profit", fmt_npr(financial["operating_profit"]))
    with f3:
        kpi_card("Profit after tax", fmt_npr(financial["profit_after_tax"]))
    with f4:
        kpi_card("Cash at year end", fmt_npr(financial["cash_end_year"]))

    left_fin, right_fin = st.columns(2)
    with left_fin:
        fin_df = pd.DataFrame({
            "Metric": ["Assets", "Current Liabilities", "Non-current Liabilities", "Equity"],
            "Value": [financial["assets_current"], financial["current_liabilities"], financial["non_current_liabilities"], financial["equity_current"]],
        })
        fig = px.bar(fin_df, x="Metric", y="Value", title="Balance sheet snapshot")
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)
    with right_fin:
        profit_df = pd.DataFrame({
            "Year": ["FY 2078/79", "FY 2079/80"],
            "Profit After Tax": [financial["profit_after_tax_previous"], financial["profit_after_tax"]],
        })
        fig = px.bar(profit_df, x="Year", y="Profit After Tax", text_auto=True, title="Loss improvement year over year")
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)

st.markdown("### Analyst takeaways")
if sector == "International":
    st.markdown(
        """
        1. International reliability is strong overall, but punctuality is materially weaker.
        2. Magh is the clearest trough month for traffic.
        3. Delay mix is dominated by immigration and SUBS rather than engineering.
        4. Market share remains well below the 2020 peak.
        """
    )
elif sector == "Domestic":
    st.markdown(
        """
        1. Domestic volume is much smaller and more volatile than international operations.
        2. Weather is the main operational risk for both delays and cancellations.
        3. Punctuality improves strongly in Asar despite a sharp drop in flights.
        4. Domestic market share remains very low.
        """
    )
else:
    st.markdown(
        """
        1. International operations carry nearly all passenger and freight volume.
        2. Domestic disruptions are more weather-driven, while international delays are more process-driven.
        3. The business still posts a net loss despite positive operating profit.
        4. The dashboard suggests a split management focus: commercial optimization internationally and reliability/risk control domestically.
        """
    )

st.divider()
st.caption("Deployment-ready Streamlit app. Use the included README for local run and hosting steps.")
