from pathlib import Path


import pandas as pd
import streamlit as st



ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "data" / "cookie_cats.csv"


@st.cache_data
def load_data() -> pd.DataFrame:
    data = pd.read_csv(SOURCE)
    data = data[data["sum_gamerounds"] < 40000].copy()
    data["Segment"] = pd.cut(
        data["sum_gamerounds"],
        bins=[-1, 0, 10, 50, 200, float("inf")],
        labels=["0 rounds", "1-10", "11-50", "51-200", "200+"],
        ordered=True,
    )
    return data


st.set_page_config(page_title="Cookie Cats A/B Test", page_icon="🍪", layout="wide")
st.title("Cookie Cats A/B Test Dashboard")
st.caption("Gate 30 versus Gate 40: retention and player engagement")

data = load_data()

with st.sidebar:
    st.header("Filters")
    versions = st.multiselect(
        "Experiment version",
        options=sorted(data["version"].unique()),
        default=sorted(data["version"].unique()),
    )
    segments = st.multiselect(
        "Player segment",
        options=data["Segment"].cat.categories.tolist(),
        default=data["Segment"].cat.categories.tolist(),
    )

filtered = data[
    data["version"].isin(versions) & data["Segment"].isin(segments)
]

players = filtered["userid"].nunique()
d1_retention = filtered["retention_1"].mean()
d7_retention = filtered["retention_7"].mean()
median_rounds = filtered["sum_gamerounds"].median()

cards = st.columns(4)
cards[0].metric("Players", f"{players:,}")
cards[1].metric("D1 Retention", f"{d1_retention:.2%}")
cards[2].metric("D7 Retention", f"{d7_retention:.2%}")
cards[3].metric("Median Game Rounds", f"{median_rounds:.0f}")

st.subheader("Retention by experiment version")
version_summary = (
    filtered.groupby("version", observed=True)[["retention_1", "retention_7"]]
    .mean()
    .rename(columns={"retention_1": "D1 Retention", "retention_7": "D7 Retention"})
)
st.bar_chart(version_summary)

left, right = st.columns(2)
with left:
    st.subheader("D7 retention by player segment")
    segment_summary = (
        filtered.groupby(["Segment", "version"], observed=True)["retention_7"]
        .mean()
        .unstack()
    )
    st.bar_chart(segment_summary)

with right:
    st.subheader("Players by segment")
    player_summary = filtered.groupby("Segment", observed=True)["userid"].nunique()
    st.bar_chart(player_summary)

st.subheader("Segment detail")
detail = (
    filtered.groupby(["Segment", "version"], observed=True)
    .agg(
        Players=("userid", "nunique"),
        D1_Retention=("retention_1", "mean"),
        D7_Retention=("retention_7", "mean"),
        Median_Rounds=("sum_gamerounds", "median"),
    )
    .reset_index()
)
for column in ("D1_Retention", "D7_Retention"):
    detail[column] = detail[column].map(lambda value: f"{value:.2%}")
st.dataframe(detail, use_container_width=True, hide_index=True)

st.subheader("Recommendation")
st.info(
    "Gate 30 is the preferred default based on the analysis: overall D7 retention "
    "is 19.02% for Gate 30 versus 18.20% for Gate 40. Confirm the decision with "
    "revenue and longer-term retention data before permanent rollout."
)

