import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Flame in Freefall", layout="wide")

st.markdown("""<style>
.block-container{padding-top:1.5rem;max-width:1500px}
div[data-testid="stVerticalBlockBorderWrapper"]{background:#131A30;border:1px solid #26304F;border-radius:14px}
.hero{border-radius:18px;padding:30px;border:1px solid #26304F;min-height:170px;
background:radial-gradient(circle at 85% 40%,#1C3769 0,transparent 55%),
radial-gradient(1.5px 1.5px at 10% 20%,#fff,transparent),
radial-gradient(1.5px 1.5px at 45% 75%,#fff,transparent),
radial-gradient(1px 1px at 65% 20%,#fff,transparent),#0E1630}
.hero h1{font-size:30px;line-height:1.2;margin:6px 0}
.stat{background:#131A30;border:1px solid #26304F;border-radius:14px;padding:16px;min-height:170px}
.stat b{display:block;font-size:34px;color:#FF9B57;margin:6px 0}
.stat span{color:#9AA6C7;font-size:13px}
.pill{display:inline-block;padding:3px 10px;border-radius:99px;font-size:12px;font-weight:600}
.ok{background:#12372A;color:#7FE3A8}.mid{background:#3A2E0B;color:#FFD36B}.no{background:#3F1613;color:#FF9A8F}
.bar{height:8px;border-radius:4px;background:#26304F;margin:4px 0 10px}
.bar i{display:block;height:8px;border-radius:4px;background:#FF7A2F}
</style>""", unsafe_allow_html=True)

df = pd.read_csv("data/catalogue.csv").fillna("not reported")
cond = pd.read_csv("data/conditions.csv")

# ---------- Row 1: hero and real stats ----------
h0, h1, h2, h3 = st.columns([2.2, 1, 1, 1])
h0.markdown("""<div class="hero"><span class="pill mid">NASA Space Apps Challenge</span>
<h1>Flame in Freefall</h1>
<div style="color:#C9D1EA">Where does NASA's microgravity fire research end, and the unknown begin? Explore studies, compare conditions and find the gaps.</div></div>""", unsafe_allow_html=True)

def stat(col, label, value, sub):
    col.markdown(f'<div class="stat"><span>{label}</span><b>{value}</b><span>{sub}</span></div>', unsafe_allow_html=True)

n = len(df)
stat(h1, "Studies catalogued", n, "in our catalogue")
stat(h2, "Report an oxygen value", f"{int((df['oxygen_reported'] == 'yes').sum())}/{n}", "studies in our catalogue")
stat(h3, "Partial-gravity studies", int((df["gravity_context"] == "partial gravity").sum()), "none in PSI per the challenge brief")

# ---------- Row 2: ranking, conditions, compare ----------
a, b, c = st.columns([1, 1.2, 1])

O2_MIN, P_MAX = 30, 70.3   # expected Moon base: 30% or more O2, up to 10.2 psi (challenge brief)

def score(row, priority):
    cc = cond[cond["title"] == row["title"]]
    topic = 2 if row["topic"] == priority else 0
    o2 = 2 if len(cc) and cc["o2_max_pct"].iloc[0] >= O2_MIN else 0
    pr = 2 if len(cc) and cc["p_min_kpa"].iloc[0] <= P_MAX else 0
    known = min(sum(row[k] == "yes" for k in ["oxygen_reported", "pressure_reported", "airflow_reported"]), 2)
    ev = {"dataset": 2, "paper": 1}.get(row["evidence_level"], 0)
    return topic, o2, pr, known, ev

with a:
    with st.container(border=True):
        st.subheader("Mission relevance ranking")
        priority = st.selectbox("Fire-safety priority", ["prevention", "detection", "suppression", "cross-cutting"])
        st.caption("Scenario: lunar habitat or pressurized rover (30% or more O2; up to 10.2 psi).")
        ranked = sorted(((sum(score(r, priority)), score(r, priority), r["title"]) for _, r in df.iterrows()), reverse=True)
        for total, parts, title in ranked[:5]:
            st.markdown(f"**{title}** &nbsp; {total}/10")
            st.markdown(f'<div class="bar"><i style="width:{total * 10}%"></i></div>', unsafe_allow_html=True)
            st.caption(f"topic {parts[0]} | oxygen {parts[1]} | pressure {parts[2]} | values reported {parts[3]} | evidence {parts[4]}")
        st.caption("A relevance score prioritises research. It is not a safety prediction.")

with b:
    with st.container(border=True):
        st.subheader("Conditions map")
        fig = go.Figure()
        fig.add_shape(type="rect", x0=30, x1=100, y0=29.6, y1=70.3,
                      line=dict(color="#FFD36B", dash="dash"), fillcolor="rgba(255,211,107,0.08)")
        for _, r in cond.iterrows():
            fig.add_trace(go.Scatter(
                x=[r.o2_min_pct, r.o2_max_pct, r.o2_max_pct, r.o2_min_pct, r.o2_min_pct],
                y=[r.p_min_kpa, r.p_min_kpa, r.p_max_kpa, r.p_max_kpa, r.p_min_kpa],
                mode="lines+markers", fill="toself", name=r.title))
        fig.update_layout(template="plotly_dark", height=330, margin=dict(l=10, r=10, t=10, b=10),
                          xaxis_title="Oxygen (%)", yaxis_title="Pressure (kPa)",
                          xaxis=dict(range=[0, 105]), yaxis=dict(range=[0, 320]),
                          legend=dict(orientation="h"))
        st.plotly_chart(fig)
        st.caption("Dashed box: expected Moon base zone. Empty space means no study in our catalogue.")

with c:
    with st.container(border=True):
        st.subheader("Compare two studies")
        titles = list(df["title"])
        s1 = st.selectbox("Study A", titles, index=0)
        s2 = st.selectbox("Study B", titles, index=min(1, len(titles) - 1))
        fields = ["fuel_phase", "oxygen_value", "pressure_value", "airflow_speed", "gravity_context", "apparatus"]
        ra = df[df["title"] == s1].iloc[0]
        rb = df[df["title"] == s2].iloc[0]
        st.dataframe(pd.DataFrame({"Field": fields, "A: " + s1: [ra[f] for f in fields],
                                   "B: " + s2: [rb[f] for f in fields]}), hide_index=True)
        if ra["fuel_phase"] != rb["fuel_phase"] or ra["apparatus"] != rb["apparatus"]:
            st.warning("Different fuel phase or apparatus: compare with care.")

# ---------- Row 3: assistant, explorer, gap map ----------
d, e, f = st.columns([1, 1.2, 1])

with d:
    with st.container(border=True):
        st.subheader("Research assistant (coming next)")
        st.chat_message("user").write("Which studies cover elevated oxygen conditions?")
        st.chat_message("assistant").write("[Answer built from retrieved NASA passages, with citations, will appear here.]")
        st.text_input("Ask a question", disabled=True, placeholder="Available once the PDF search is built")

with e:
    with st.container(border=True):
        st.subheader("Investigation explorer")
        q = st.text_input("Search title or material")
        view = df
        if q:
            m = df["title"].str.contains(q, case=False) | df["fuel_material"].str.contains(q, case=False)
            view = df[m]
        st.dataframe(view[["title", "topic", "fuel_material", "gravity_context"]], hide_index=True)
        if len(view):
            pick = st.selectbox("Study details", view["title"])
            row = df[df["title"] == pick].iloc[0]
            st.write(row["objective"])
            st.link_button("Open source", row["source_url"])
            st.caption(f"Notes: {row['notes']}")

with f:
    with st.container(border=True):
        st.subheader("Evidence gap map")
        gaps = [("Oxygen value reported", (df["oxygen_reported"] == "yes").sum()),
                ("Pressure value reported", (df["pressure_reported"] == "yes").sum()),
                ("Airflow value reported", (df["airflow_reported"] == "yes").sum()),
                ("Detection studies", (df["topic"] == "detection").sum()),
                ("Suppression studies", (df["topic"] == "suppression").sum()),
                ("Partial-gravity studies", (df["gravity_context"] == "partial gravity").sum())]
        for label, found in gaps:
            cls, sym = ("ok", "●") if found >= 2 else ("mid", "◐") if found == 1 else ("no", "○")
            st.markdown(f'{label} <span class="pill {cls}" style="float:right">{sym} {int(found)}</span>', unsafe_allow_html=True)
        st.caption("Counts in our catalogue only. Not proof that a hazard is absent.")

st.caption("Check every value against the linked NASA source. Scores and counts describe our catalogue, not NASA's full archive.")