from fastapi import FastAPI
import requests
from datetime import datetime, timezone
import os

app = FastAPI(title="Financial News Cleaning API")

# -----------------------------
# Get Finnhub API Key
# -----------------------------
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")


# -----------------------------
# Cleaning + Categorization
# -----------------------------
def clean_and_categorize_news(news_list):

    cleaned_news = []
    now = datetime.now(timezone.utc)

    for news in news_list:

        # Convert timestamp → datetime
        news_time = datetime.fromtimestamp(
            news["datetime"],
            tz=timezone.utc
        )

        # Calculate hours difference
        hours_old = (
            now - news_time
        ).total_seconds() / 3600

        # ❌ Remove news older than 24 hours
        if hours_old > 24:
            continue

        # 🏷️ Categorize by freshness
        if hours_old <= 1:
            category = "Breaking"
        elif hours_old <= 6:
            category = "Very Recent"
        elif hours_old <= 12:
            category = "Recent"
        else:
            category = "Today"

        # ✅ Cleaned news object
        cleaned_news.append({
            "headline": news.get("headline"),
            "summary": news.get("summary"),
            "source": news.get("source"),
            "url": news.get("url"),
            "image": news.get("image"),
            "published_at": news_time.isoformat(),
            "hours_ago": round(hours_old, 2),
            "category": category
        })

    return cleaned_news


# -----------------------------
# API Route
# -----------------------------
@app.get("/financial-news")
def get_financial_news(category: str = "general"):

    # Check API key
    if not FINNHUB_API_KEY:
        return {"error": "Finnhub API key not set"}

    # Finnhub endpoint
    url = (
        f"https://finnhub.io/api/v1/news"
        f"?category={category}"
        f"&token={FINNHUB_API_KEY}"
    )

    response = requests.get(url)

    # Error handling
    if response.status_code != 200:
        return {
            "error": "Failed to fetch news",
            "status_code": response.status_code,
            "details": response.text
        }

    # Convert → Python JSON
    news_data = response.json()

    # Clean + categorize
    cleaned_news = clean_and_categorize_news(news_data)

    # Final response
    return {
        "total_news": len(cleaned_news),
        "news": cleaned_news
    }