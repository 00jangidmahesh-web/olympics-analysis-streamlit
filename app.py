import streamlit as st
import pandas as pd
import preprocessor, helper
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.figure_factory as ff
import os
import gdown

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(
    page_title="Olympics Data Analysis Dashboard",
    page_icon="🏅",
    layout="wide"
)

# -------------------------------
# Load Dataset from Google Drive
# -------------------------------
DATA_PATH = "athlete_events.csv"
FILE_ID = "1AQN6Xab3FASVNz97q4vL3fylVFybc3Cu"

if not os.path.exists(DATA_PATH):
    url = f"https://drive.google.com/uc?id={FILE_ID}"
    gdown.download(url, DATA_PATH, quiet=False)

df = pd.read_csv(DATA_PATH)
region_df = pd.read_csv("noc_regions.csv")
df = preprocessor.preprocess(df, region_df)

# -------------------------------
# Sidebar
# -------------------------------
st.sidebar.title("🏅 Olympics Analysis")
st.sidebar.image(
    "https://e7.pngegg.com/pngimages/1020/402/png-clipart-2024-summer-olympics-brand-circle-area-olympic-rings-olympics-logo-text-sport.png"
)

user_menu = st.sidebar.radio(
    "Select an Option",
    ("Medal Tally", "Overall Analysis", "Country-wise Analysis", "Athlete wise Analysis")
)

# -------------------------------
# Medal Tally
# -------------------------------
if user_menu == "Medal Tally":
    st.sidebar.header("Medal Tally")
    years, country = helper.country_year_list(df)

    selected_year = st.sidebar.selectbox("Select Year", years)
    selected_country = st.sidebar.selectbox("Select Country", country)

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

# -------------------------------
# Overall Analysis
# -------------------------------
if user_menu == "Overall Analysis":
    st.title("📊 Top Statistics")

    editions = df["Year"].nunique() - 1
    cities = df["City"].nunique()
    sports = df["Sport"].nunique()
    events = df["Event"].nunique()
    athletes = df["Name"].nunique()
    nations = df["region"].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("Editions", editions)
    col2.metric("Hosts", cities)
    col3.metric("Sports", sports)

    col1, col2, col3 = st.columns(3)
    col1.metric("Events", events)
    col2.metric("Nations", nations)
    col3.metric("Athletes", athletes)

    st.subheader("Participating Nations Over the Years")
    nations_over_time = helper.data_over_time(df, "region")
    st.plotly_chart(px.line(nations_over_time, x="Edition", y="region"), use_container_width=True)

    st.subheader("Events Over the Years")
    events_over_time = helper.data_over_time(df, "Event")
    st.plotly_chart(px.line(events_over_time, x="Edition", y="Event"), use_container_width=True)

    st.subheader("Athletes Over the Years")
    athlete_over_time = helper.data_over_time(df, "Name")
    st.plotly_chart(px.line(athlete_over_time, x="Edition", y="Name"), use_container_width=True)

    st.subheader("Number of Events per Sport Over Time")
    fig, ax = plt.subplots(figsize=(18, 18))
    temp = df.drop_duplicates(["Year", "Sport", "Event"])
    sns.heatmap(
        temp.pivot_table(index="Sport", columns="Year", values="Event", aggfunc="count")
        .fillna(0)
        .astype(int),
        ax=ax
    )
    st.pyplot(fig)

    st.subheader("Most Successful Athletes")
    sport_list = sorted(df["Sport"].unique().tolist())
    sport_list.insert(0, "Overall")
    selected_sport = st.selectbox("Select a Sport", sport_list)
    st.table(helper.most_successful(df, selected_sport))

# -------------------------------
# Country-wise Analysis
# -------------------------------
if user_menu == "Country-wise Analysis":
    st.sidebar.title("Country-wise Analysis")

    country_list = sorted(df["region"].dropna().unique().tolist())
    selected_country = st.sidebar.selectbox("Select a Country", country_list)

    st.title(f"{selected_country} Medal Tally Over the Years")
    country_df = helper.yearwise_medal_tally(df, selected_country)
    st.plotly_chart(px.line(country_df, x="Year", y="Medal"), use_container_width=True)

    st.subheader(f"{selected_country} Excels in These Sports")
    pt = helper.country_event_heatmap(df, selected_country)
    fig, ax = plt.subplots(figsize=(18, 18))
    sns.heatmap(pt, annot=True, ax=ax)
    st.pyplot(fig)

    st.subheader(f"Top 10 Athletes of {selected_country}")
    st.table(helper.most_successful_countrywise(df, selected_country))

# -------------------------------
# Athlete-wise Analysis
# -------------------------------
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
    fig.update_layout(height=600)
    st.title("Age Distribution of Athletes")
    st.plotly_chart(fig, use_container_width=True)

    st.title("Height vs Weight")
    sport_list = sorted(df["Sport"].unique().tolist())
    sport_list.insert(0, "Overall")
    selected_sport = st.selectbox("Select Sport", sport_list)

    temp_df = helper.weight_v_height(df, selected_sport)
    fig, ax = plt.subplots()
    sns.scatterplot(
        data=temp_df,
        x="Weight",
        y="Height",
        hue="Medal",
        style="Sex",
        s=60,
        ax=ax
    )
    st.pyplot(fig)

    st.title("Men vs Women Participation Over the Years")
    final = helper.men_vs_women(df)
    st.plotly_chart(px.line(final, x="Year", y=["Male", "Female"]), use_container_width=True)

