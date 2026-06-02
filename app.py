import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
import math
from PIL import Image
import time
import base64
from datetime import datetime
import urllib.parse

# ── PAGE CONFIG ───────────────────────────────────────────────
st.set_page_config(
    page_title="ForkScore",
    page_icon="🍴",
    layout="wide"
)

# ── GLOBAL STYLES ─────────────────────────────────────────────
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"], [class*="st-"], h1, h2, h3, h4, p, div, span, button {
        font-family: 'Poppins', sans-serif !important;
    }

    /* ALL buttons red by default */
    div.stButton > button {
        background: linear-gradient(135deg, #D32F2F, #7B0000) !important;
        color: white !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 10px 28px !important;
        cursor: pointer !important;
        font-family: Poppins, sans-serif !important;
        box-shadow: 0 4px 14px rgba(211, 47, 47, 0.4) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        width: 100% !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(211, 47, 47, 0.6) !important;
        color: white !important;
    }

    /* Nav buttons override — plain text, no background, no border */
    .nav-btn div.stButton > button {
        background: transparent !important;
        color: #AAAAAA !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 8px 18px !important;
        box-shadow: none !important;
        width: auto !important;
        transform: none !important;
    }
    .nav-btn div.stButton > button:hover {
        background: transparent !important;
        color: white !important;
        box-shadow: none !important;
        transform: none !important;
        border: none !important;
    }

    /* Hide sidebar collapse tooltip */
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stSidebarCollapseButton"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# ── DATABASE CONNECTION ───────────────────────────────────────
conn = psycopg2.connect(
    st.secrets["DATABASE_URL"],
    sslmode="require"
)

# ── SESSION STATE ─────────────────────────────────────────────
if "results" not in st.session_state:
    st.session_state.results = None
if "selected_city" not in st.session_state:
    st.session_state.selected_city = ""
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "surprise" not in st.session_state:
    st.session_state.surprise = None

# ── HELPERS ───────────────────────────────────────────────────
def load_image_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_b64 = load_image_b64("final fork score logo.png")

def format_time(t):
    if pd.isna(t):
        return None
    parts = str(t).strip().split(":")
    if len(parts) == 2:
        hour = int(parts[0])
        minute = parts[1].zfill(2)
        period = "AM" if hour < 12 else "PM"
        if hour == 0:
            hour = 12
        elif hour > 12:
            hour = hour - 12
        return f"{hour}:{minute} {period}"
    return t

# ── NAV BAR ───────────────────────────────────────────────────
def show_navbar():
    col_logo, col_spacer, col_home, col_search, col_explore, col_about = st.columns([5, 2, 1, 1, 1, 1])

    with col_logo:
        st.markdown(f"""
            <div style='display:flex; align-items:center; gap:18px; padding:10px 0;'>
                <img src='data:image/png;base64,{logo_b64}' width='70'/>
                <div>
                    <p style='color:white; font-size:36px; font-weight:800;
                        margin:0; line-height:1.1; font-family:Poppins,sans-serif;'>ForkScore</p>
                    <p style='color:#888888; font-size:14px; margin:0;
                        font-family:Poppins,sans-serif;'>Find Food. Score Better.</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_home:
        st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
        if st.button("Home", key="nav_home"):
            st.session_state.page = "landing"
            st.session_state.results = None
            st.session_state.surprise = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_search:
        st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
        if st.button("Search", key="nav_search"):
            st.session_state.page = "search"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_explore:
        st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
        if st.button("Explore", key="nav_explore"):
            st.session_state.page = "explore"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_about:
        st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
        if st.button("About", key="nav_about"):
            st.session_state.page = "about"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()


# ══════════════════════════════════════════════════════════════
# LANDING PAGE
# ══════════════════════════════════════════════════════════════
if st.session_state.page == "landing":

    st.markdown("""
        <style>[data-testid="stSidebar"] {display: none;}</style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown(f"""
            <div style='text-align:center; padding-top:60px;'>
                <img src='data:image/png;base64,{logo_b64}' width='120' style='margin-bottom:16px;'/>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <h1 style='color:white; font-size:64px; font-weight:800; margin:0;
                text-align:center; font-family:Poppins,sans-serif;'>ForkScore</h1>
            <p style='color:#888888; font-size:20px; margin:8px 0 24px 0;
                text-align:center; font-family:Poppins,sans-serif;'>Find Food. Score Better.</p>
            <p style='color:#CCCCCC; font-size:16px; line-height:1.8;
                text-align:center; margin-bottom:40px; font-family:Poppins,sans-serif;'>
                Can't decide where to eat? Find the best meal for your budget. Every time.<br><br>
                ForkScore ranks restaurants by <strong style="color:white;">quality and consistency</strong>.
            </p>
        """, unsafe_allow_html=True)

        col_a, col_b, col_c = st.columns([1, 2, 1])
        with col_b:
            if st.button("🍴 Find My Next Meal", use_container_width=True, key="landing_btn"):
                st.session_state.page = "search"
                st.rerun()

        st.markdown("""
            <p style='color:#555555; font-size:13px; text-align:center; margin-top:16px;'>
                Powered by 38,000+ real restaurants from the Yelp Open Dataset
            </p>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# SEARCH PAGE
# ══════════════════════════════════════════════════════════════
elif st.session_state.page == "search":

    show_navbar()

    st.sidebar.markdown(f"""
        <img src='data:image/png;base64,{logo_b64}' width='60'/>
    """, unsafe_allow_html=True)
    st.sidebar.title("Find Restaurants")
    st.sidebar.markdown("---")

    cities_query = "SELECT DISTINCT city FROM restaurants ORDER BY city"
    cities_df = pd.read_sql(cities_query, conn)
    city_list = cities_df["city"].tolist()
    selected_city = st.sidebar.selectbox("City", city_list)

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Price Range**")
    price_options = {
        "\$": 1,
        "\$\$": 2,
        "\$\$\$": 3,
        "\$\$\$\$": 4
    }
    selected_prices = []
    for label, value in price_options.items():
        if st.sidebar.checkbox(label, value=True):
            selected_prices.append(value)

    st.sidebar.markdown("---")
    cuisines_query = """
        SELECT DISTINCT cuisine_type FROM categories
        WHERE cuisine_type IN (
            'Afghan','African','American','Arabian','Argentine','Armenian',
            'Asian Fusion','Australian','Austrian','Bangladeshi','Barbeque',
            'Belgian','Brasseries','Brazilian','British','Burmese',
            'Cajun','Cambodian','Caribbean','Chinese','Colombian','Cuban',
            'Czech','Dominican','Egyptian','Ethiopian','Filipino',
            'Fish & Chips','Fondue','French','Gastropubs','German','Greek',
            'Halal','Hawaiian','Himalayan','Hot Dogs','Hot Pot','Hungarian',
            'Indian','Indonesian','Irish','Italian','Japanese','Jewish',
            'Kebab','Korean','Kosher','Latin American','Lebanese','Malaysian',
            'Mediterranean','Mexican','Middle Eastern','Mongolian','Moroccan',
            'Nepalese','New American','Nicaraguan','Noodles','Pakistani',
            'Pan Asian','Persian','Peruvian','Polish','Portuguese',
            'Puerto Rican','Ramen','Russian','Salvadoran','Scottish',
            'Seafood','Senegalese','Singaporean','Soul Food','Southern',
            'Spanish','Sri Lankan','Steakhouses','Sushi Bars','Syrian',
            'Taiwanese','Tapas Bars','Tapas Small Plates','Tex-Mex','Thai',
            'Turkish','Ukrainian','Uzbek','Vegan','Vegetarian','Venezuelan',
            'Vietnamese','Acai Bowls','Comfort Food','Creperies','Dim Sum',
            'Empanadas','Falafel','Gluten-Free','International','Izakaya',
            'Modern European','Pacific Northwest','Poke','Salad',
            'Sandwiches','Scandinavian','Soup','Szechuan','Tacos',
            'Taquerias','Waffles','Wraps','Pho','Banh Mi',
            'Korean BBQ','Small Plates','Farm to Table','Organic',
            'Fine Dining','Fast Casual','Breakfast & Brunch','Brunch',
            'Deli','Bakery','Ice Cream','Gelato','Bubble Tea',
            'Boba','Smoothies','Cafe','Steakhouse','Chophouse',
            'Oyster Bar','Sushi','Pizza','Pasta','Burgers',
            'Wings','Fried Chicken','Burritos','Quesadillas',
            'Dumplings','Stew','Chili','Curry','Tapas',
            'Mezze','Charcuterie','Creole','Gumbo',
            'New Mexican Cuisine','Honduran','Guatemalan','Jamaican',
            'Haitian','Ecuadorian','Chilean','Georgian','Eritrean',
            'Somali','Nigerian','Kenyan','South African',
            'Cantonese','Shanghainese','Hakka','Tibetan','Laotian'
        )
        ORDER BY cuisine_type
    """
    cuisines_df = pd.read_sql(cuisines_query, conn)
    cuisine_list = cuisines_df["cuisine_type"].tolist()
    selected_cuisines = st.sidebar.multiselect(
        "Cuisine", cuisine_list, placeholder="All Cuisines"
    )

    st.sidebar.markdown("---")
    min_rating = st.sidebar.slider("Minimum Rating", 1.0, 5.0, 3.0, step=0.5)
    st.sidebar.markdown("---")
    open_now = st.sidebar.toggle("Open Now")
    st.sidebar.markdown("---")
    search = st.sidebar.button("🍴 Find Restaurants", use_container_width=True, key="find_btn")

    if search:
        if not selected_prices:
            st.warning("Please select at least one price range.")
        else:
            now = datetime.now()
            current_day = now.strftime("%A")
            current_time = now.strftime("%H:%M")

            query = """
                SELECT DISTINCT
                    r.name, r.city, r.address, r.latitude, r.longitude,
                    rt.overall_rating, rt.review_count,
                    p.price_level, p.fork_score,
                    h.open_time, h.close_time
                FROM restaurants r
                JOIN ratings rt ON r.id = rt.restaurant_id
                JOIN pricing p ON r.id = p.restaurant_id
                JOIN categories c ON r.id = c.restaurant_id
                LEFT JOIN hours h ON r.id = h.restaurant_id AND h.day_of_week = %s
                WHERE r.city = %s
                AND p.price_level = ANY(%s)
                AND rt.overall_rating >= %s
            """
            params = [current_day, selected_city, selected_prices, min_rating]

            if selected_cuisines:
                query += " AND c.cuisine_type = ANY(%s)"
                params.append(selected_cuisines)

            if open_now:
                query += """
                    AND r.id IN (
                        SELECT restaurant_id FROM hours WHERE day_of_week = %s
                        AND (LPAD(SPLIT_PART(open_time,':',1),2,'0')||':'||LPAD(SPLIT_PART(open_time,':',2),2,'0')) <= %s
                        AND (LPAD(SPLIT_PART(close_time,':',1),2,'0')||':'||LPAD(SPLIT_PART(close_time,':',2),2,'0')) >= %s
                    )
                """
                params.extend([current_day, current_time, current_time])

            query += " ORDER BY p.fork_score DESC"

            with st.spinner("🍴 Scoring restaurants for you..."):
                results = pd.read_sql(query, conn, params=params)
                time.sleep(1)

            st.session_state.results = results
            st.session_state.selected_city = selected_city
            st.session_state.surprise = None

    if st.session_state.results is not None:
        results = st.session_state.results.copy()
        city_display = st.session_state.selected_city

        st.info("💡 Changed your filters? Click **Find Restaurants** to update results.")

        if len(results) == 0:
            st.warning("No restaurants found. Try adjusting your filters.")
        else:
            sort_by = st.radio("Sort by", ["Fork Score", "Rating", "Review Count"], horizontal=True)
            if sort_by == "Fork Score":
                results = results.sort_values("fork_score", ascending=False)
            elif sort_by == "Rating":
                results = results.sort_values("overall_rating", ascending=False)
            else:
                results = results.sort_values("review_count", ascending=False)

            results["price_level"] = results["price_level"].map({1:"$",2:"$$",3:"$$$",4:"$$$$"})
            results.columns = ["Name","City","Address","Latitude","Longitude",
                               "Rating","Reviews","Price","Fork Score","Open Time","Close Time"]

            st.markdown("---")
            col_s1, col_s2, col_s3, col_s4 = st.columns([2, 3, 3, 2])
            with col_s2:
                if st.button("🎲 Surprise Me!", use_container_width=True, key="surprise_btn"):
                    surprise = results.head(20).sample(1).iloc[0]
                    st.session_state.surprise = surprise
            with col_s3:
                if st.button("🔄 Reroll", use_container_width=True, key="reroll_btn"):
                    surprise = results.head(20).sample(1).iloc[0]
                    st.session_state.surprise = surprise
            st.markdown("---")

            if st.session_state.get("surprise") is not None:
                surprise = st.session_state.surprise
                score = surprise["Fork Score"]
                s_color = "#2E7D32" if score >= 4.0 else "#F57F17" if score >= 3.0 else "#D32F2F"
                s_label = "Excellent" if score >= 4.0 else "Great" if score >= 3.0 else "Good"
                s_emoji = "🟢" if score >= 4.0 else "🟡" if score >= 3.0 else "🔴"
                open_fmt = format_time(surprise["Open Time"])
                close_fmt = format_time(surprise["Close Time"])
                hours_display = f"🕐 Today: {open_fmt} — {close_fmt}" if open_fmt and close_fmt else "🕐 Hours not available"

                st.markdown(f"""
                    <div style='background:linear-gradient(135deg,#1A1A2E,#16213E);
                        border-radius:16px; padding:24px; margin-bottom:24px;
                        border:2px solid #D32F2F; box-shadow:0 0 24px rgba(211,47,47,0.4);'>
                        <p style='color:#D32F2F; font-size:14px; font-weight:700; margin:0 0 8px 0;
                            font-family:Poppins,sans-serif; text-transform:uppercase; letter-spacing:2px;'>
                            🎲 Your ForkScore Pick</p>
                        <div style='display:flex; justify-content:space-between; align-items:center;'>
                            <div>
                                <h2 style='color:white; margin:0; font-size:26px; font-family:Poppins,sans-serif;'>{surprise["Name"]}</h2>
                                <p style='color:#AAAAAA; margin:4px 0; font-size:15px; font-family:Poppins,sans-serif;'>📍 {surprise["Address"]}, {surprise["City"]}</p>
                                <p style='color:#AAAAAA; margin:4px 0; font-size:15px; font-family:Poppins,sans-serif;'>⭐ {surprise["Rating"]} &nbsp;&nbsp; 💬 {int(surprise["Reviews"])} reviews &nbsp;&nbsp; 💰 {surprise["Price"]}</p>
                                <p style='color:#AAAAAA; margin:4px 0; font-size:13px; font-family:Poppins,sans-serif;'>{hours_display}</p>
                            </div>
                            <div style='text-align:center; min-width:100px;'>
                                <p style='color:{s_color}; font-size:42px; font-weight:bold; margin:0; font-family:Poppins,sans-serif;'>{score}</p>
                                <p style='color:{s_color}; font-size:13px; font-weight:bold; margin:0; font-family:Poppins,sans-serif;'>{s_emoji} {s_label}</p>
                                <p style='color:#666666; font-size:11px; margin:0; font-family:Poppins,sans-serif;'>Fork Score</p>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
                <div style='background:linear-gradient(135deg,#D32F2F,#7B0000);
                    border-radius:12px; padding:20px 24px; margin-bottom:24px; text-align:center;'>
                    <h2 style='color:white; margin:0; font-size:24px; font-family:Poppins,sans-serif;'>
                        🔥 {len(results)} restaurants ranked for you in {city_display}
                    </h2>
                    <p style='color:#FFCDD2; margin:4px 0; font-size:14px; font-family:Poppins,sans-serif;'>
                        Sorted by Fork Score — quality and consistency, not popularity
                    </p>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("""
                <style>
                .restaurant-card {
                    background-color:white; border-radius:12px;
                    padding:20px 24px; margin-bottom:12px;
                    display:flex; justify-content:space-between; align-items:center;
                    box-shadow:0 2px 8px rgba(0,0,0,0.3);
                    transition:transform 0.2s ease, box-shadow 0.2s ease, border-left 0.2s ease;
                    border-left:4px solid transparent;
                }
                .restaurant-card:hover {
                    transform:translateY(-3px);
                    box-shadow:0 8px 24px rgba(211,47,47,0.3);
                    border-left:4px solid #D32F2F;
                }
                </style>
            """, unsafe_allow_html=True)

            for _, row in results.iterrows():
                score = row["Fork Score"]
                score_color = "#2E7D32" if score >= 4.0 else "#F57F17" if score >= 3.0 else "#D32F2F"
                score_label = "Excellent" if score >= 4.0 else "Great" if score >= 3.0 else "Good"
                score_emoji = "🟢" if score >= 4.0 else "🟡" if score >= 3.0 else "🔴"
                open_fmt = format_time(row["Open Time"])
                close_fmt = format_time(row["Close Time"])
                hours_display = f"🕐 Today: {open_fmt} — {close_fmt}" if open_fmt and close_fmt else "🕐 Hours not available"

                st.markdown(f"""
                    <div class='restaurant-card'>
                        <div>
                            <h3 style='color:#1A1A1A; margin:0; font-size:22px; font-family:Poppins,sans-serif;'>{row["Name"]}</h3>
                            <p style='color:#666666; margin:4px 0; font-size:16px; font-family:Poppins,sans-serif;'>📍 {row["Address"]}, {row["City"]}</p>
                            <p style='color:#666666; margin:4px 0; font-size:16px; font-family:Poppins,sans-serif;'>⭐ {row["Rating"]} &nbsp;&nbsp; 💬 {int(row["Reviews"])} reviews &nbsp;&nbsp; 💰 {row["Price"]}</p>
                            <p style='color:#888888; margin:4px 0; font-size:14px; font-family:Poppins,sans-serif;'>{hours_display}</p>
                        </div>
                        <div style='text-align:center; min-width:90px;'>
                            <p style='color:{score_color}; font-size:36px; font-weight:bold; margin:0; font-family:Poppins,sans-serif;'>{score}</p>
                            <p style='color:{score_color}; font-size:12px; font-weight:bold; margin:0; font-family:Poppins,sans-serif;'>{score_emoji} {score_label}</p>
                            <p style='color:#AAAAAA; font-size:11px; margin:0; font-family:Poppins,sans-serif;'>Fork Score</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# EXPLORE PAGE
# ══════════════════════════════════════════════════════════════
elif st.session_state.page == "explore":

    show_navbar()

    st.markdown("""
        <h2 style='color:white; font-size:36px; font-weight:800;
            font-family:Poppins,sans-serif; margin-bottom:8px;'>📊 Explore</h2>
        <p style='color:#AAAAAA; font-size:16px; font-family:Poppins,sans-serif; margin-bottom:32px;'>
            Interactive map and charts — search for a city first, then explore the data here.
        </p>
    """, unsafe_allow_html=True)

    if st.session_state.results is None:
        st.info("👈 Go to Search first and find restaurants in a city — then come back here to explore.")
    else:
        st.success(f"✅ Results loaded for **{st.session_state.selected_city}**. Charts and map coming soon!")


# ══════════════════════════════════════════════════════════════
# ABOUT PAGE
# ══════════════════════════════════════════════════════════════
elif st.session_state.page == "about":

    show_navbar()

    st.markdown("""
        <style>
        .info-card {
            background-color:#1E1E1E; border-radius:12px;
            padding:24px; margin-bottom:16px; border-left:4px solid #D32F2F;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <h2 style='color:white; font-size:36px; font-weight:800;
            font-family:Poppins,sans-serif; margin-bottom:8px;'>What is the Fork Score?</h2>
        <p style='color:#AAAAAA; font-size:16px; font-family:Poppins,sans-serif; margin-bottom:32px;'>
            Every restaurant on ForkScore gets a Fork Score — a transparent, data-driven number
            that tells you how good and how trustworthy a restaurant actually is.
        </p>

        <div class='info-card'>
            <h3 style='color:#D32F2F; font-size:20px; font-weight:700;
                margin:0 0 12px 0; font-family:Poppins,sans-serif;'>The Problem with Yelp</h3>
            <p style='color:#CCCCCC; font-size:15px; line-height:1.7; margin:0; font-family:Poppins,sans-serif;'>
                Yelp ranks restaurants by popularity, advertising spend, and user engagement — not actual quality.
                A mediocre restaurant with 3,000 reviews consistently outranks a genuinely great one with 80 reviews.
                The algorithm is a black box.
            </p>
        </div>

        <div class='info-card'>
            <h3 style='color:#D32F2F; font-size:20px; font-weight:700;
                margin:0 0 12px 0; font-family:Poppins,sans-serif;'>The Formula</h3>
            <p style='color:#CCCCCC; font-size:15px; line-height:1.7; margin:0 0 16px 0; font-family:Poppins,sans-serif;'>
                The Fork Score combines rating and review reliability into one transparent number.
            </p>
            <div style='background:#2A2A2A; border-radius:8px; padding:16px 24px; text-align:center; margin-bottom:16px;'>
                <p style='color:white; font-size:22px; font-weight:700; margin:0; font-family:Courier New,monospace;'>
                    Fork Score = Rating × Reliability
                </p>
            </div>
            <p style='color:#CCCCCC; font-size:15px; line-height:1.7; margin:0; font-family:Poppins,sans-serif;'>
                <strong style='color:white;'>Rating</strong> — raw Yelp star rating from 1.0 to 5.0.<br><br>
                <strong style='color:white;'>Reliability</strong> — log-scaled score from 0 to 1 based on review count.
                8 reviews = 0.35. 500+ reviews = 1.0.
            </p>
        </div>

        <div class='info-card'>
            <h3 style='color:#D32F2F; font-size:20px; font-weight:700;
                margin:0 0 12px 0; font-family:Poppins,sans-serif;'>Why Log Scaling?</h3>
            <p style='color:#CCCCCC; font-size:15px; line-height:1.7; margin:0; font-family:Poppins,sans-serif;'>
                Going from 10 to 50 reviews is a big deal. Going from 450 to 490 barely matters.
                Log scaling reflects how trust actually builds over time.
            </p>
        </div>

        <div class='info-card'>
            <h3 style='color:#D32F2F; font-size:20px; font-weight:700;
                margin:0 0 12px 0; font-family:Poppins,sans-serif;'>How Price Works</h3>
            <p style='color:#CCCCCC; font-size:15px; line-height:1.7; margin:0; font-family:Poppins,sans-serif;'>
                Price is not part of the Fork Score formula. Set your budget first and Fork Score
                ranks every restaurant within that budget by quality and consistency.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class='info-card'>
            <h3 style='color:#D32F2F; font-size:20px; font-weight:700;
                margin:0 0 16px 0; font-family:Poppins,sans-serif;'>Fork Score in Action</h3>
    """, unsafe_allow_html=True)

    example_df = pd.DataFrame({
        "Restaurant": ["Proven Taco Spot", "New Taco Spot", "Italian Bistro"],
        "Rating": ["4.5 ⭐", "4.5 ⭐", "4.7 ⭐"],
        "Reviews": ["400", "8", "300"],
        "Reliability": ["0.96", "0.35", "0.92"],
        "Fork Score": ["4.32", "1.58", "4.32"]
    })
    st.dataframe(example_df, use_container_width=True, hide_index=True)

    st.markdown("""
        <p style='color:#AAAAAA; font-size:14px; font-family:Poppins,sans-serif; margin-top:12px;'>
            The proven taco spot and the Italian bistro tie even though the bistro has a higher raw rating —
            because the taco spot has far more reviews confirming its quality.
        </p>
        </div>

        <div style='background:linear-gradient(135deg,#D32F2F,#7B0000);
            border-radius:12px; padding:24px; margin-top:24px; text-align:center;'>
            <h3 style='color:white; font-size:20px; font-weight:700;
                margin:0 0 8px 0; font-family:Poppins,sans-serif;'>
                No black box. No ads. No sponsored results.
            </h3>
            <p style='color:#FFCDD2; font-size:15px; margin:0; font-family:Poppins,sans-serif;'>
                Just a transparent formula that rewards quality and consistency — every time.
            </p>
        </div>
    """, unsafe_allow_html=True)