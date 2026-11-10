import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Conditions Map", layout="wide")
st.title("Conditions Map")
st.caption("Oxygen and pressure conditions covered by the catalogued studies. Empty space means no study in our catalogue.")

df = pd.read_csv("data/conditions.csv")
catalogue = pd.read_csv("data/catalogue.csv")

fig = go.Figure()

# Expected Moon base and rover zone (from the challenge brief; illustrative bounds)
fig.add_shape(type="rect", x0=30, x1=100, y0=29.6, y1=70.3,
              line=dict(color="#FFD36B", dash="dash"), fillcolor="rgba(255,211,107,0.08)")
fig.add_annotation(x=65, y=76, text="Expected Moon base and rover zone (30% or more O2; up to 10.2 psi)",
                   showarrow=False, font=dict(color="#FFD36B"))

refs = [("Earth sea level", 21, 101.3), ("Spacesuit", 100, 29.6)]
fig.add_trace(go.Scatter(
    x=[r[1] for r in refs], y=[r[2] for r in refs], mode="markers+text",
    text=[r[0] for r in refs], textposition="top center",
    marker=dict(size=13, color="#5CC8FF", symbol="diamond"), name="Reference points"))

for _, r in df.iterrows():
    x = [r.o2_min_pct, r.o2_max_pct, r.o2_max_pct, r.o2_min_pct, r.o2_min_pct]
    y = [r.p_min_kpa, r.p_min_kpa, r.p_max_kpa, r.p_max_kpa, r.p_min_kpa]
    fig.add_trace(go.Scatter(
        x=x, y=y, mode="lines+markers+text", fill="toself", name=r.title,
        text=[r.title, "", "", "", ""], textposition="top right",
        marker=dict(size=9), hovertext=r.note, hoverinfo="name+text"))

fig.update_layout(template="plotly_dark", height=560,
                  xaxis_title="Oxygen concentration (% by volume)",
                  yaxis_title="Pressure (kPa)",
                  xaxis=dict(range=[0, 105]), yaxis=dict(range=[0, 320]))
st.plotly_chart(fig)

st.caption("Boxes show the overall range of conditions in each study, not every combination tested.")

plotted = set(df["title"])
missing = [t for t in catalogue["title"] if t not in plotted]
if missing:
    st.info("Not plotted (no oxygen or pressure values in our record): " + ", ".join(missing))

with st.expander("Units and sources"):
    st.write("1 atm = 101.325 kPa. 1 psi = 6.895 kPa. Earth sea level is 14.7 psi. A spacesuit is 4.3 psi. "
             "The Moon base zone follows the challenge brief, which says it will likely be 30% oxygen or more at 10.2 psi or less.")
    st.dataframe(df, hide_index=True)