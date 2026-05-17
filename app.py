import sys
sys.path.append("src")

import streamlit as st
import pandas as pd
from database import DatabaseManager

st.set_page_config(
    page_title="NIFTY Sentiment Dashboard",
    layout="wide"
)

st.title("NIFTY 50 Stocks Sentiment Dashboard")

# ---------------- DATABASE ----------------

db_manager = DatabaseManager()

article_data = db_manager.get_articles()
ticker_metadata = db_manager.get_ticker_metadata()

# ---------------- SIDEBAR ----------------

st.sidebar.header("Filters")

date_range = st.sidebar.selectbox(
    "Select Time Range",
    ["Past 24 Hours", "Past 7 Days", "Past 1 Month"]
)

# ---------------- DATE FILTER ----------------

article_data["date_posted"] = pd.to_datetime(
    article_data["date_posted"]
)

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

# ---------------- AGGREGATE ----------------

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

# ---------------- RENAME ----------------

final_df.rename(
    columns={
        "compound_sentiment": "Sentiment Score",
        "positive_sentiment": "Positive",
        "negative_sentiment": "Negative",
        "neutral_sentiment": "Neutral",
    },
    inplace=True,
)

# ---------------- DISPLAY ----------------

st.subheader(f"Showing Data: {date_range}")

st.dataframe(final_df)

# ---------------- NEWS VIEW ----------------

st.subheader("Stock News")

selected_stock = st.selectbox(
    "Select Stock",
    final_df["ticker"].unique()
)

stock_news = filtered_articles[
    filtered_articles["ticker"] == selected_stock
]

st.dataframe(
    stock_news[
        [
            "headline",
            "source",
            "date_posted",
            "compound_sentiment",
        ]
    ]
)
