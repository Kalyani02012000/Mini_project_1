# 1. Setup and Imports
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import mysql.connector

# 2. Load Data Function
@st.cache_data
def load_data():
    mydb = mysql.connector.connect(
        host='localhost',
        user='root',
        password='1q2w3e',
        database='imdb'
    )
    query = "SELECT * FROM all_movies;"
    df = pd.read_sql(query, mydb)
    mydb.close()
    return df

# 3. Load Data
df = load_data()
df["DurationHrs"] = df["Duration"] / 60

# 4. Radio Button for Page Selection
page = st.sidebar.radio(
    "Select a Page",
   ("📊 Data Analysis & Visualizations", "🎯 Interactive Filtering & Analysis")
)

# -------------------- PAGE 1 -----------------------
if page == "📊 Data Analysis & Visualizations":
    st.title("📊 Data Analysis and Visualizations")

    st.subheader("🎥 Top 10 Movies by Rating")
    top_rating = df.sort_values(by="Rating", ascending=False).head(10)
    st.bar_chart(top_rating.set_index("Title")["Rating"])

    st.subheader("🔥 Top 10 Movies by Voting Count")
    top_votes = df.sort_values(by="Voting", ascending=False).head(10)
    st.bar_chart(top_votes.set_index("Title")["Voting"])

    st.subheader("📚 Genre Distribution")
    genre_count = df['Genre'].value_counts()
    st.bar_chart(genre_count)

    st.subheader("⏱️ Average Duration by Genre")
    avg_duration = df.groupby('Genre')['DurationHrs'].mean().sort_values()
    st.bar_chart(avg_duration)

    st.subheader("📈 Average Voting by Genre")
    avg_votes = df.groupby('Genre')['Voting'].mean()
    st.bar_chart(avg_votes)

    st.subheader("🎯 Rating Distribution")
    fig, ax = plt.subplots()
    sns.histplot(df["Rating"], kde=True, ax=ax)
    st.pyplot(fig)

    st.subheader("🏆 Top-rated Movie per Genre")
    top_by_genre = df.loc[df.groupby('Genre')['Rating'].idxmax()]
    st.dataframe(top_by_genre[["Title", "Genre", "Rating"]])

    st.subheader("💥 Most Popular Genres by Voting")
    genre_votes = df.groupby('Genre')['Voting'].sum()
    st.plotly_chart(px.pie(values=genre_votes, names=genre_votes.index))

    st.subheader("📏 Shortest and Longest Movies")
    min_duration = df.loc[df["DurationHrs"].idxmin()]
    max_duration = df.loc[df["DurationHrs"].idxmax()]
    st.write("🎬 Shortest Movie:", min_duration["Title"], "-", round(min_duration["DurationHrs"], 2), "hrs")
    st.write("🎬 Longest Movie:", max_duration["Title"], "-", round(max_duration["DurationHrs"], 2), "hrs")

    st.subheader("🔥 Avg Ratings by Genre (Heatmap)")
    genre_rating = df.groupby('Genre')['Rating'].mean().reset_index()
    heatmap_data = genre_rating.pivot_table(values='Rating', index='Genre', aggfunc='mean')
    fig, ax = plt.subplots()
    sns.heatmap(heatmap_data, annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig)

    st.subheader("🧪 Correlation: Ratings vs Voting")
    fig, ax = plt.subplots()
    sns.scatterplot(x="Rating", y="Voting", data=df, ax=ax)
    st.pyplot(fig)

# -------------------- PAGE 2 -----------------------
elif page == "🎯 Interactive Filtering & Analysis":
    st.title("🎯 Interactive Filtering and Analysis")

    st.sidebar.header("🔍 Filter Movies")

    with st.sidebar.form(key="filter_form"):
        duration_filter = st.radio("Duration (Hours)", ["All", "< 2", "2 - 3", "> 3"])
        rating_filter = st.slider("Minimum Rating", 0.0, 10.0, 0.0, 0.1)
        voting_filter = st.number_input("Minimum Votes", min_value=0, value=0)
        genre_filter = st.multiselect("Select Genres", df['Genre'].unique())
        submit_button = st.form_submit_button(label="Apply Filters 🎯")

    if submit_button:
        filtered_df = df.copy()

        # Apply duration filter
        if duration_filter != "All":
            if duration_filter == "< 2":
                filtered_df = filtered_df[filtered_df["DurationHrs"] < 2]
            elif duration_filter == "2 - 3":
                filtered_df = filtered_df[(filtered_df["DurationHrs"] >= 2) & (filtered_df["DurationHrs"] <= 3)]
            else:
                filtered_df = filtered_df[filtered_df["DurationHrs"] > 3]

        filtered_df = filtered_df[filtered_df["Rating"] >= rating_filter]
        filtered_df = filtered_df[filtered_df["Voting"] >= voting_filter]

        if genre_filter:
            filtered_df = filtered_df[filtered_df["Genre"].isin(genre_filter)]

        st.subheader("🎬 Filtered Movies")
        st.dataframe(filtered_df)

        # Visualizations
        st.subheader("🎥 Top 10 Movies by Rating (Filtered)")
        top_rating = filtered_df.sort_values(by="Rating", ascending=False).head(10)
        st.bar_chart(top_rating.set_index("Title")["Rating"])

        st.subheader("🔥 Top 10 Movies by Voting Count (Filtered)")
        top_votes = filtered_df.sort_values(by="Voting", ascending=False).head(10)
        st.bar_chart(top_votes.set_index("Title")["Voting"])

        st.subheader("📚 Genre Distribution (Filtered)")
        genre_count = filtered_df['Genre'].value_counts()
        st.bar_chart(genre_count)

        st.subheader("🧪 Correlation: Ratings vs Voting (Filtered)")
        fig, ax = plt.subplots()
        sns.scatterplot(x="Rating", y="Voting", data=filtered_df, ax=ax)
        st.pyplot(fig)

    else:
        st.info("Please apply filters from the sidebar to view filtered visualizations 🎯")
