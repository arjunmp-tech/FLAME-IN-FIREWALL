import pandas as pd
import streamlit as st

st.set_page_config(page_title="Flame in Freefall", layout="wide")
st.title("Flame in Freefall")
st.caption("NASA combustion research explorer. Check every value against the linked source.")

df = pd.read_csv("data/catalogue.csv").fillna("not reported")

c1, c2, c3 = st.columns(3)
query = c1.text_input("Search title or material")
topic = c2.selectbox("Topic", ["all"] + sorted(df["topic"].unique()))
gravity = c3.selectbox("Gravity", ["all"] + sorted(df["gravity_context"].unique()))

view = df
if query:
    match = view["title"].str.contains(query, case=False, na=False) | \
            view["fuel_material"].str.contains(query, case=False, na=False)
    view = view[match]
if topic != "all":
    view = view[view["topic"] == topic]
if gravity != "all":
    view = view[view["gravity_context"] == gravity]

st.write(f"{len(view)} of {len(df)} investigations shown")

key_cols = ["title", "topic", "fuel_material", "oxygen_value",
            "pressure_value", "airflow_speed", "gravity_context", "evidence_level"]
st.dataframe(view[key_cols], hide_index=True)

st.subheader("Study details")
if len(view) == 0:
    st.info("No studies match your filters.")
    st.stop()

choice = st.selectbox("Open a study", view["title"])
row = view[view["title"] == choice].iloc[0]

st.markdown(f"### {row['title']}")
st.write(row["objective"])

left, right = st.columns(2)
with left:
    st.markdown("**Test conditions**")
    st.write(f"Fuel or material: {row['fuel_material']}")
    st.write(f"Fuel phase: {row['fuel_phase']}")
    st.write(f"Sample shape and size: {row['sample_shape_size']}")
    st.write(f"Oxygen: {row['oxygen_value']}")
    st.write(f"Pressure: {row['pressure_value']}")
    st.write(f"Airflow: {row['airflow_speed']}")
with right:
    st.markdown("**Setup and measurements**")
    st.write(f"Gravity context: {row['gravity_context']}")
    st.write(f"Apparatus: {row['apparatus']}")
    st.write(f"Sensors: {row['sensors']}")
    st.write(f"Measured: {row['measurement_type']}")
    st.write(f"Evidence level: {row['evidence_level']}")

st.link_button("Open source", row["source_url"])
st.warning(f"Notes: {row['notes']}")
st.info("'not reported' means the source did not state the value. It is not a zero and not a guess.")