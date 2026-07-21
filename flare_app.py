import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="FLARE — Ghana", layout="wide", page_icon="🛰️")

# ---------------------------------------------------------------
# Neighbourhoods: name, city, lat, lon, population (thousands)
# ---------------------------------------------------------------
NEIGHBOURHOODS = [
    ("Alajo",  "Accra",  5.585, -0.216, 42),
    ("Nima",   "Accra",  5.583, -0.197, 80),
    ("Aboabo", "Kumasi", 6.700, -1.605, 48),
]

@st.cache_data
def build_data(seed: int = 11):
    rng = np.random.default_rng(seed)
    days = pd.date_range(datetime.today() - timedelta(days=59),
                         datetime.today(), freq="D")
    series, latest = {}, []
    for (name, city, lat, lon, pop) in NEIGHBOURHOODS:
        base  = rng.uniform(3, 9)
        surge = int(rng.integers(22, 52))
        rain  = base + np.maximum(0, rng.normal(0, 5, len(days)))
        rain[surge:surge + 4] += rng.uniform(40, 90)          # flood event

        drain = rng.uniform(0.82, 0.90)
        water = np.zeros(len(days)); w = rng.uniform(5, 15)
        for i, r in enumerate(rain):
            w = min(100, w * drain + r * 1.1)                 # standing water
            water[i] = w

        pools = np.clip((water - 45) / 55 * 100, 0, 100)      # breeding pools

        risk = np.zeros(len(days))
        for i in range(len(days)):
            j = max(0, i - 14)                                # ~2-week lag
            risk[i] = np.clip(pools[j] * 0.8 + water[i] * 0.15
                              + rng.normal(0, 4), 0, 100)

        series[name] = pd.DataFrame(
            {"date": days, "rain": rain, "water": water,
             "pools": pools, "risk": risk})
        latest.append(dict(neighbourhood=name, city=city, lat=lat, lon=lon,
                           pop=pop, risk=risk[-1], pools=pools[-1],
                           water=water[-1]))
    return series, pd.DataFrame(latest)

def level(v):
    return ("ALERT"   if v >= 70 else
            "WARNING" if v >= 50 else
            "WATCH"   if v >= 30 else "NORMAL")

COLOR = {"ALERT": "#d62728", "WARNING": "#ff7f0e",
         "WATCH": "#f4c542", "NORMAL": "#2ca02c"}

series, latest = build_data()
latest["level"] = latest.risk.apply(level)

# ---------------------------------------------------------------
# Header
# ---------------------------------------------------------------
st.title("🛰️ FLARE — Ghana")
st.markdown("**Flood-Linked Alert for Regional Epidemics** · "
            "flood-triggered malaria early warning for Accra & Kumasi")

# ---------------------------------------------------------------
# Top-line status
# ---------------------------------------------------------------
cols = st.columns(len(latest))
for c, (_, row) in zip(cols, latest.iterrows()):
    c.metric(f"{row.neighbourhood} · {row.city}",
             f"{row.risk:.0f}/100",
             row.level)
    c.markdown(
        f"<div style='height:6px;border-radius:3px;"
        f"background:{COLOR[row.level]}'></div>",
        unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------------
# Map
# ---------------------------------------------------------------
left, right = st.columns([1.1, 1])

with left:
    st.subheader("Risk map")
    fig = go.Figure(go.Scattermapbox(
        lat=latest.lat, lon=latest.lon,
        mode="markers+text",
        marker=dict(size=latest.risk / 2 + 14,
                    color=[COLOR[l] for l in latest.level]),
        text=latest.neighbourhood,
        textposition="top center",
        hovertext=[f"{r.neighbourhood} ({r.city}) · {r.level} · risk {r.risk:.0f}"
                   for _, r in latest.iterrows()],
        hoverinfo="text"))
    fig.update_layout(mapbox_style="carto-positron",
                      mapbox_zoom=6.2,
                      mapbox_center={"lat": 6.1, "lon": -0.9},
                      margin=dict(l=0, r=0, t=0, b=0), height=430)
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Neighbourhood detail")
    pick = st.selectbox("Select a neighbourhood", latest.neighbourhood)
    df = series[pick]
    row = latest[latest.neighbourhood == pick].iloc[0]

    trend = go.Figure()
    trend.add_trace(go.Scatter(x=df.date, y=df.pools, name="Breeding pools",
                               line=dict(color="#1f77b4")))
    trend.add_trace(go.Scatter(x=df.date, y=df.risk, name="Malaria risk",
                               line=dict(color=COLOR[row.level], width=3)))
    trend.add_hline(y=70, line_dash="dash", line_color="#d62728",
                    annotation_text="Alert threshold")
    trend.update_layout(height=430, margin=dict(l=0, r=0, t=10, b=0),
                        legend=dict(orientation="h", y=1.12),
                        yaxis_title="index (0–100)")
    st.plotly_chart(trend, use_container_width=True)

# ---------------------------------------------------------------
# How it works
# ---------------------------------------------------------------
st.divider()
st.markdown(
    "**How FLARE works.** Sentinel-1 radar detects new standing water after a "
    "flood. FLARE flags the resulting mosquito breeding pools and projects the "
    "malaria risk ~2 weeks ahead. When risk is projected to cross the threshold, "
    "the alert lets NMEP Larval Source Management teams larvicide the new pools "
    "*before* adult mosquitoes emerge."
    "<br><br><b>Demo note:</b> figures are simulated to illustrate the concept. "
    "In production, standing water comes from Sentinel-1 SAR (10 m, all-weather), "
    "rainfall from GPM/IMERG, malaria surveillance from NMEP / Ghana Health "
    "Service, and entomological ground-truth from KCCR. Alerts are tied to NMEP's "
    "existing Larval Source Management response.",
    unsafe_allow_html=True)
