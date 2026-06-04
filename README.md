# ForkScore 🍴

**Find Food. Score Better.**

A restaurant discovery app that ranks restaurants by quality and consistency — not popularity or ad spend.

🔗 **Live App:** [forkscore.streamlit.app](https://forkscore.streamlit.app)

---

## What is ForkScore?

ForkScore fixes a core problem with Yelp: popular restaurants outrank genuinely great ones just because they have more reviews or pay for advertising. ForkScore uses a transparent, data-driven formula to rank restaurants by actual quality.

**Fork Score = Rating × Reliability**

- **Rating** — the raw Yelp star rating (1.0–5.0)
- **Reliability** — a log-scaled score based on review count. A restaurant with 8 reviews scores 0.35. One with 500+ reviews scores 1.0.

No black box. No ads. No sponsored results.

---

## Features

### 🔍 Search
- Filter by city, cuisine, price range, and minimum rating
- Toggle "Open Now" to only show restaurants currently open
- Sort results by Fork Score, Rating, or Review Count
- Color-coded score cards — 🟢 Excellent, 🟡 Great, 🔴 Good

### 🎲 Surprise Me
- Randomly picks a top-ranked restaurant from your results
- Reroll as many times as you want

### 📊 Explore
Interactive data visualizations for every city search:
- **Restaurant Map** — every restaurant plotted on a dark map, color coded by Fork Score tier, sized by review count, fully hoverable
- **Top Cuisines by Fork Score** — horizontal bar chart showing which cuisines score highest in that city
- **Rating vs Review Count** — scatter plot proving why raw star ratings are misleading without review volume
- **Does Price = Quality?** — bar chart comparing average Fork Score across price tiers ($, $$, $$$, $$$$)

### ℹ️ About
Full explanation of the Fork Score formula, reliability table, and worked examples.

---

## Tech Stack

| Layer | Tool |
|---|---|
| Data | Yelp Open Dataset (38,000+ restaurants) |
| Database | PostgreSQL (Supabase) |
| Backend | Python, Pandas, psycopg2 |
| Visualizations | Plotly Express |
| Frontend | Streamlit |
| Deployment | Streamlit Cloud |

---

## The Formula

```
Fork Score = Rating × Reliability
```

Reliability is log-scaled based on review count:

| Reviews | Reliability | Trust Level |
|---|---|---|
| 8 | 0.35 | Barely proven |
| 50 | 0.63 | Getting reliable |
| 150 | 0.81 | Fairly reliable |
| 400 | 0.96 | Very reliable |
| 500+ | 1.00 | Fully trusted |

**Why log scaling?** Going from 10 to 50 reviews is a big deal — the restaurant is becoming proven. Going from 450 to 490 barely matters. Log scaling reflects how trust actually builds over time.

**Why not include price in the formula?** Price is a budget filter, not a quality signal. A great taco spot and a great steakhouse shouldn't be penalized for being in different price tiers. You set your budget first, then Fork Score ranks everything within it.

---

## Running Locally

1. Clone the repo
   ```
   git clone https://github.com/BrianXNguyenn/forkscore.git
   cd forkscore
   ```

2. Install dependencies
   ```
   pip install -r requirements.txt
   ```

3. Create `.streamlit/secrets.toml` with your Supabase connection string:
   ```toml
   DATABASE_URL = "your-supabase-connection-string"
   ```

4. Run the app
   ```
   streamlit run app.py
   ```

---

## Project Structure

```
forkscore/
├── app.py                      # Main application
├── requirements.txt            # Python dependencies
├── final fork score logo.png   # App logo
└── .streamlit/
    └── secrets.toml            # Database connection (not committed)
```

---

## Database Schema

```
restaurants   — id, name, city, address, latitude, longitude
ratings       — restaurant_id, overall_rating, review_count
pricing       — restaurant_id, price_level, fork_score
categories    — restaurant_id, cuisine_type
hours         — restaurant_id, day_of_week, open_time, close_time
```

---

*Powered by the Yelp Open Dataset. Built as a data science capstone project.*
