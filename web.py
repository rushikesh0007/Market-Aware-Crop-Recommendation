import streamlit as st
import pandas as pd
from recommender import recommend_crop, model

# set sensible starting values so the fields aren't empty on first load
_DEFAULTS = dict(N=90.0, P=42.0, K=43.0, temperature=21.0,
                 humidity=82.0, ph=6.5, rainfall=202.0)
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# cache the dataset so we don't re-read it from disk on every button click
@st.cache_data
def load_crop_dataset():
    return pd.read_csv("data/Crop_recommendation.csv")

st.title("🌾 Market-Aware Crop Recommendation System")

st.divider()

st.subheader("🌱 Soil & Weather Parameters")

btn_col1, btn_col2 = st.columns(2)

with btn_col1:
    # fill all fields with a real row from the training dataset — useful for demos
    if st.button("🎲 Generate Sample Data", help="Populate fields with a random row from the crop dataset", use_container_width=True):
        df = load_crop_dataset()
        row = df.sample(1).iloc[0]
        st.session_state["N"]           = float(row["N"])
        st.session_state["P"]           = float(row["P"])
        st.session_state["K"]           = float(row["K"])
        st.session_state["temperature"] = float(row["temperature"])
        st.session_state["humidity"]    = float(row["humidity"])
        st.session_state["ph"]          = float(row["ph"])
        st.session_state["rainfall"]    = float(row["rainfall"])
        st.info(f"Loaded sample row — crop label in dataset: **{row['label']}**")

with btn_col2:
    # find a row where the model is torn between crops — more interesting to show
    if st.button("🧪 Generate Interesting Scenario", help="Find a row where the model is uncertain between multiple crops", use_container_width=True):
        df = load_crop_dataset()
        features = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
        found_row = None

        # shuffle and scan until we find a close call (low confidence or small gap between top 2)
        shuffled = df.sample(frac=1).reset_index(drop=True)
        for _, candidate in shuffled.iterrows():
            sample = pd.DataFrame([candidate[features].values], columns=features)
            probs = model.predict_proba(sample)[0]
            sorted_probs = sorted(probs, reverse=True)
            top_prob = sorted_probs[0]
            gap = sorted_probs[0] - sorted_probs[1]
            if top_prob < 0.60 or gap < 0.20:
                found_row = candidate
                found_top = round(top_prob * 100, 1)
                found_gap = round(gap * 100, 1)
                break

        if found_row is not None:
            st.session_state["N"]           = float(found_row["N"])
            st.session_state["P"]           = float(found_row["P"])
            st.session_state["K"]           = float(found_row["K"])
            st.session_state["temperature"] = float(found_row["temperature"])
            st.session_state["humidity"]    = float(found_row["humidity"])
            st.session_state["ph"]          = float(found_row["ph"])
            st.session_state["rainfall"]    = float(found_row["rainfall"])
            st.info(
                f"🧪 Uncertain scenario found — dataset label: **{found_row['label']}** | "
                f"Top probability: **{found_top}%** | Gap to 2nd: **{found_gap}%**"
            )
        else:
            st.warning("Could not find an uncertain scenario in the dataset. Try again!")

# two-column layout for the input fields
col1, col2 = st.columns(2)

with col1:
    N = st.number_input("Nitrogen (N)",    min_value=0.0,   max_value=140.0, step=1.0,  key="N")
    P = st.number_input("Phosphorus (P)",  min_value=0.0,   max_value=145.0, step=1.0,  key="P")
    K = st.number_input("Potassium (K)",   min_value=0.0,   max_value=205.0, step=1.0,  key="K")

with col2:
    temperature = st.number_input("Temperature (°C)", min_value=-10.0, max_value=60.0,  step=0.1, key="temperature")
    humidity    = st.number_input("Humidity (%)",      min_value=0.0,   max_value=100.0, step=0.1, key="humidity")
    ph          = st.number_input("pH",                min_value=0.0,   max_value=14.0,  step=0.1, key="ph")
    rainfall    = st.number_input("Rainfall (mm)",     min_value=0.0,   max_value=300.0, step=1.0, key="rainfall")

if st.button("Recommend Crop"):

    results, best_crop = recommend_crop(N, P, K, temperature, humidity, ph, rainfall)

    st.subheader("Top 3 Suitable Crops")

    if not results:
        st.warning("No crops could be recommended. Please check your inputs.")
    else:
        for crop, prob, price, score in results:
            if price is None:
                st.write(f"{crop} — {prob}% probability — ⚠️ Price unavailable")
            else:
                st.write(f"{crop} — {prob}% probability — ₹{price} — Score: {score}")

        st.success(f"Best Crop to Grow: {best_crop}")

    # only draw the chart if at least one crop has a score to compare
    scored_results = [(c, prob, p, s) for c, prob, p, s in results if s is not None]
    if scored_results:
        df_chart = pd.DataFrame(scored_results, columns=["Crop", "Probability", "Price", "Score"])
        st.subheader("Market Score Comparison (Probability × Price)")
        st.bar_chart(df_chart.set_index("Crop")["Score"])
    else:
        st.info("No price data available to display chart.")