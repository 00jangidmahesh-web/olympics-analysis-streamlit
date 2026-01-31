import streamlit as st
import pandas as pd
import preprocessor, helper
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.figure_factory as ff
import os
import gdown

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="Olympics Data Analysis Dashboard",
    page_icon="🏅",
    layout="wide"
)

# ---------------- Load Dataset ----------------
DATA_PATH = "athlete_events.csv"
FILE_ID = "1AQN6Xab3FASVNz97q4vL3fylVFybc3Cu"

if not os.path.exists(DATA_PATH):
    gdown.download(f"https://drive.google.com/uc?id={FILE_ID}", DATA_PATH, quiet=False)

df = pd.read_csv(DATA_PATH)
region_df = pd.read_csv("noc_regions.csv")
df = preprocessor.preprocess(df, region_df)

# ---------------- Sidebar ----------------
st.sidebar.title("🏅 Olympics Analysis")
st.sidebar.image(
    "https://e7.pngegg.com/pngimages/1020/402/png-clipart-2024-summer-olympics-brand-circle-area-olympic-rings-olympics-logo-text-sport.png"
)

user_menu = st.sidebar.radio(
    "Select an Option",
    ("Medal Tally", "Overall Analysis", "Country-wise Analysis", "Athlete wise Analysis")
)

# ---------------- Medal Tally ----------------
if user_menu == "Medal Tally":
    st.sidebar.header("Medal Tally")
    years, countries = helper.country_year_list(df)

    selected_year = st.sidebar.selectbox("Select Year", years)
    selected_country = st.sidebar.selectbox("Select Country", countries)

    medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)

    if selected_year == "Overall" and selected_country == "Overall":
        st.title("Overall Medal Tally")
    elif selected_year != "Overall" and selected_country == "Overall":
        st.title(f"Medal Tally in {selected_year} Olympics")
    elif selected_year == "Overall" and selected_country != "Overall":
        st.title(f"{selected_country} Overall Performance")
    else:
        st.title(f"{selected_country} Performance in {selected_year} Olympics")

    st.table(medal_tally)

# ---------------- Overall Analysis ----------------
if user_menu == "Overall Analysis":
    st.title("📊 Top Statistics")

    col1, col2, col3 = st.columns(3)
    col1.metric("Editions", df["Year"].nunique() - 1)
    col2.metric("Hosts", df["City"].nunique())
    col3.metric("Sports", df["Sport"].nunique())

    col1, col2, col3 = st.columns(3)
    col1.metric("Events", df["Event"].nunique())
    col2.metric("Nations", df["region"].nunique())
    col3.metric("Athletes", df["Name"].nunique())

    st.plotly_chart(
        px.line(helper.data_over_time(df, "region"), x="Edition", y="region"),
        use_container_width=True
    )

# ---------------- Country-wise Analysis ----------------
if user_menu == "Country-wise Analysis":
    country = st.sidebar.selectbox(
        "Select Country", sorted(df["region"].dropna().unique())
    )

    country_df = helper.yearwise_medal_tally(df, country)
    st.plotly_chart(px.line(country_df, x="Year", y="Medal"), use_container_width=True)

# ---------------- Athlete-wise Analysis ----------------
if user_menu == "Athlete wise Analysis":
    athlete_df = df.drop_duplicates(subset=["Name", "region"])

    x1 = athlete_df["Age"].dropna()
    x2 = athlete_df[athlete_df["Medal"] == "Gold"]["Age"].dropna()
    x3 = athlete_df[athlete_df["Medal"] == "Silver"]["Age"].dropna()
    x4 = athlete_df[athlete_df["Medal"] == "Bronze"]["Age"].dropna()

    fig = ff.create_distplot(
        [x1, x2, x3, x4],
        ["Overall", "Gold", "Silver", "Bronze"],
        show_hist=False,
        show_rug=False
    )
    st.plotly_chart(fig, use_container_width=True)

