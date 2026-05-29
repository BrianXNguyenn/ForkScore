# ForkScore 🍴

**Find Food. Score Better.**

A restaurant discovery app that ranks restaurants by quality and consistency — not popularity or ad spend.

🔗 **Live App:** [forkscore.streamlit.app](https://forkscore.streamlit.app)

---

## What is ForkScore?

ForkScore fixes a core problem with Yelp: popular restaurants outrank genuinely great ones just because they have more reviews. ForkScore uses a transparent, data-driven formula to rank restaurants by actual quality.

**Fork Score = Rating × Reliability**

- **Rating** — the raw Yelp star rating (1.0–5.0)
- **Reliability** — a log-scaled score based on review count. A restaurant with 8 reviews scores 0.35. One with 500+ reviews scores 1.0.

---

## Features

- Filter by city, cuisine, price range, and minimum rating
- Toggle "Open Now" to only show restaurants currently open
- Sort results by Fork Score, Rating, or Review Count
- 🎲 Surprise Me — randomly picks a top-ranked restaurant for you

---

## Tech Stack

| Layer | Tool |
|---|---|
| Data | Yelp Open Dataset (38,000+ restaurants) |
| Database | PostgreSQL (Supabase) |
| Backend | Python, Pandas, psycopg2 |
| Frontend | Streamlit |
| Deployment | Streamlit Cloud |

---

## Running Locally

1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Create `.streamlit/secrets.toml` with your database URL:
```toml
DATABASE_URL = "your-supabase-connection-string"
```
4. Run: `streamlit run app.py`
