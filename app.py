import streamlit as st
import pandas as pd
from src.database import DatabaseManager

st.set_page_config(
    page_title="NIFTY Sentiment Dashboard",
    layout="wide"
)

st.title("NIFTY 50 Stocks Sentiment Analyzer")

# ---------------- DATABASE ----------------

db_manager = DatabaseManager()

article_data = db_manager.get_articles()
ticker_metadata = db_manager.get_ticker_metadata()

# ---------------- FILTERS ----------------

st.sidebar.header("Filters")

date_range = st.sidebar.selectbox(
    "Pick the Date Range",
    ["Past 24 Hours", "Past 7 Days", "Past 1 Month"]
)

# ---------------- DATE FILTER ----------------

article_data["date_posted"] = pd.to_datetime(article_data["date_posted"])

now = pd.Timestamp.now()

if date_range == "Past 24 Hours":
    filtered_articles = article_data[
        article_data["date_posted"] >= now - pd.Timedelta(hours=24)
    ]

elif date_range == "Past 7 Days":
    filtered_articles = article_data[
        article_data["date_posted"] >= now - pd.Timedelta(days=7)
    ]

else:
    filtered_articles = article_data[
        article_data["date_posted"] >= now - pd.Timedelta(days=30)
    ]

# ---------------- SENTIMENT AGGREGATION ----------------

ticker_scores = (
    filtered_articles[
        [
            "ticker",
            "neutral_sentiment",
            "positive_sentiment",
            "negative_sentiment",
            "compound_sentiment",
        ]
    ]
    .groupby("ticker")
    .mean()
    .reset_index()
)

final_df = pd.merge(
    ticker_metadata,
    ticker_scores,
    on="ticker",
    how="inner"
)

# ---------------- DISPLAY ----------------

st.subheader(f"Showing Data For: {date_range}")

st.dataframe(final_df)

# ---------------- STOCK NEWS ----------------

st.subheader("Stock Specific News")

selected_ticker = st.selectbox(
    "Select Stock",
    final_df["ticker"].unique()
)

news_df = filtered_articles[
    filtered_articles["ticker"] == selected_ticker
]

st.dataframe(
    news_df[
        [
            "headline",
            "source",
            "date_posted",
            "compound_sentiment",
        ]
    ]
)