import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
import math
from PIL import Image
import time
import base64
from datetime import datetime

# Setup browser
st.set_page_config(
    page_title="ForkScore",
    page_icon="🍴",
    layout="wide"
)

# import Poppins font and apply globally
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"], [class*="st-"], h1, h2, h3, h4, p, div, span, button {
        font-family: 'Poppins', sans-serif !important;
    }
    </style>
""", unsafe_allow_html=True)

# Connect to postgresql
conn = psycopg2.connect(
    host="localhost",
    database="forkscore",
    user="postgres",
    password="Namtrinh15121128"
)

# initialize session state
if "results" not in st.session_state:
    st.session_state.results = None
if "selected_city" not in st.session_state:
    st.session_state.selected_city = ""
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "surprise" not in st.session_state:
    st.session_state.surprise = None

# helper function to load image as base64
def load_image_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_b64 = load_image_b64("final fork score logo.png")

# time format helper
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

# ── LANDING PAGE ─────────────────────────────────────────────
if st.session_state.page == "landing":

    st.markdown("""
        <style>
        [data-testid="stSidebar"] {display: none;}
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 3, 1])

    with col2:
        st.markdown(f"""
            <div style='text-align: center; padding-top: 60px;'>
                <img src='data:image/png;base64,{logo_b64}' width='120' style='margin-bottom: 16px;'/>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <h1 style='
                color: white;
                font-size: 64px;
                font-weight: 800;
                margin: 0;
                padding: 0;
                text-align: center;
                font-family: Poppins, sans-serif;
            '>ForkScore</h1>
            <p style='
                color: #888888;
                font-size: 20px;
                margin: 8px 0 24px 0;
                text-align: center;
                font-family: Poppins, sans-serif;
            '>Find Food. Score Better.</p>
            <p style='
                color: #CCCCCC;
                font-size: 16px;
                line-height: 1.8;
                text-align: center;
                margin-bottom: 40px;
                font-family: Poppins, sans-serif;
            '>
                Can't decide where to eat? Find the best meal for your budget. Every time.<br><br>
                ForkScore ranks restaurants by <strong style="color: white;">quality and consistency</strong>.
            </p>
        """, unsafe_allow_html=True)

        st.markdown("""
            <style>
            div.stButton > button {
                background: linear-gradient(135deg, #D32F2F, #7B0000);
                color: white;
                font-size: 18px;
                font-weight: 700;
                border: none;
                border-radius: 50px;
                padding: 14px 48px;
                min-width: 280px;
                width: auto;
                display: block;
                margin: 0 auto;
                cursor: pointer;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
                box-shadow: 0 4px 20px rgba(211, 47, 47, 0.5);
                white-space: nowrap;
                font-family: Poppins, sans-serif;
            }
            div.stButton > button:hover {
                transform: translateY(-3px);
                box-shadow: 0 8px 30px rgba(211, 47, 47, 0.7);
                color: white;
            }
            </style>
        """, unsafe_allow_html=True)

        col_a, col_b, col_c = st.columns([1, 2, 1])
        with col_b:
            if st.button("🍴 Find My Next Meal", use_container_width=True):
                st.session_state.page = "search"
                st.rerun()

        st.markdown("""
            <p style='color: #555555; font-size: 13px; text-align: center; margin-top: 16px;'>
                Powered by 38,000+ real restaurants from the Yelp Open Dataset
            </p>
        """, unsafe_allow_html=True)

# ── SEARCH PAGE ───────────────────────────────────────────────
elif st.session_state.page == "search":

    col1, col2 = st.columns([1, 10])
    with col1:
        st.markdown(f"""
            <img src='data:image/png;base64,{logo_b64}' width='100'/>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div style='display: flex; flex-direction: column; justify-content: center; height: 100%;'>
                <h1 style='color: white; margin: 0; padding: 0; font-size: 48px; font-family: Poppins, sans-serif;'>ForkScore</h1>
                <p style='color: #888888; font-size: 18px; margin: 0; padding: 0; font-family: Poppins, sans-serif;'>Find Food. Score Better.</p>
            </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.sidebar.markdown(f"""
        <img src='data:image/png;base64,{logo_b64}' width='60'/>
    """, unsafe_allow_html=True)
    st.sidebar.title("Find Restaurants")
    st.sidebar.markdown("---")

    cities_query = """
        SELECT DISTINCT city
        FROM restaurants
        ORDER BY city
    """
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
        SELECT DISTINCT cuisine_type 
        FROM categories 
        WHERE cuisine_type IN (
            'Afghan', 'African', 'American', 'Arabian', 'Argentine', 'Armenian',
            'Asian Fusion', 'Australian', 'Austrian', 'Bangladeshi', 'Barbeque',
            'Belgian', 'Brasseries', 'Brazilian', 'British', 'Burmese',
            'Cajun', 'Cambodian', 'Caribbean', 'Chinese', 'Colombian', 'Cuban',
            'Czech', 'Dominican', 'Egyptian', 'Ethiopian', 'Filipino',
            'Fish & Chips', 'Fondue', 'French', 'Gastropubs', 'German', 'Greek',
            'Halal', 'Hawaiian', 'Himalayan', 'Hot Dogs', 'Hot Pot', 'Hungarian',
            'Indian', 'Indonesian', 'Irish', 'Italian', 'Japanese', 'Jewish',
            'Kebab', 'Korean', 'Kosher', 'Latin American', 'Lebanese', 'Malaysian',
            'Mediterranean', 'Mexican', 'Middle Eastern', 'Mongolian', 'Moroccan',
            'Nepalese', 'New American', 'Nicaraguan', 'Noodles', 'Pakistani',
            'Pan Asian', 'Persian', 'Peruvian', 'Polish', 'Portuguese',
            'Puerto Rican', 'Ramen', 'Russian', 'Salvadoran', 'Scottish',
            'Seafood', 'Senegalese', 'Singaporean', 'Soul Food', 'Southern',
            'Spanish', 'Sri Lankan', 'Steakhouses', 'Sushi Bars', 'Syrian',
            'Taiwanese', 'Tapas Bars', 'Tapas Small Plates', 'Tex-Mex', 'Thai',
            'Turkish', 'Ukrainian', 'Uzbek', 'Vegan', 'Vegetarian', 'Venezuelan',
            'Vietnamese', 'Acai Bowls', 'Comfort Food', 'Creperies', 'Dim Sum',
            'Empanadas', 'Falafel', 'Gluten-Free', 'International', 'Izakaya',
            'Modern European', 'Pacific Northwest', 'Poke', 'Salad',
            'Sandwiches', 'Scandinavian', 'Soup', 'Szechuan', 'Tacos',
            'Taquerias', 'Waffles', 'Wraps', 'Pho', 'Banh Mi',
            'Korean BBQ', 'Small Plates', 'Farm to Table', 'Organic',
            'Fine Dining', 'Fast Casual', 'Breakfast & Brunch', 'Brunch',
            'Deli', 'Bakery', 'Ice Cream', 'Gelato', 'Bubble Tea',
            'Boba', 'Smoothies', 'Cafe', 'Steakhouse', 'Chophouse',
            'Oyster Bar', 'Sushi', 'Pizza', 'Pasta', 'Burgers',
            'Wings', 'Fried Chicken', 'Burritos', 'Quesadillas',
            'Dumplings', 'Stew', 'Chili', 'Curry', 'Tapas',
            'Mezze', 'Charcuterie', 'Fondue', 'Creole', 'Gumbo',
            'New Mexican Cuisine', 'Honduran', 'Guatemalan', 'Jamaican',
            'Haitian', 'Ecuadorian', 'Chilean', 'Georgian', 'Eritrean',
            'Somali', 'Nigerian', 'Kenyan', 'South African', 'Kosher',
            'Cantonese', 'Shanghainese', 'Hakka', 'Tibetan', 'Laotian'
        )
        ORDER BY cuisine_type
    """
    cuisines_df = pd.read_sql(cuisines_query, conn)
    cuisine_list = cuisines_df["cuisine_type"].tolist()
    selected_cuisines = st.sidebar.multiselect(
        "Cuisine",
        cuisine_list,
        placeholder="All Cuisines"
    )

    st.sidebar.markdown("---")
    min_rating = st.sidebar.slider("Minimum Rating", 1.0, 5.0, 3.0, step=0.5)

    st.sidebar.markdown("---")
    open_now = st.sidebar.toggle("Open Now")

    st.sidebar.markdown("""
        <style>
        div.stButton > button {
            background-color: #D32F2F;
            color: white;
            font-size: 18px;
            font-weight: bold;
            border: none;
            border-radius: 8px;
            padding: 12px;
            width: 100%;
            cursor: pointer;
            font-family: Poppins, sans-serif;
        }
        div.stButton > button:hover {
            background-color: #B71C1C;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)

    if st.sidebar.button("❓ What is Fork Score?"):
        st.session_state.page = "forkscore"
        st.session_state.surprise = None
        st.rerun()

    if st.sidebar.button("← Back to Home"):
        st.session_state.page = "landing"
        st.session_state.results = None
        st.session_state.surprise = None
        st.rerun()

    st.sidebar.markdown("---")
    search = st.sidebar.button("🍴 Find Restaurants", use_container_width=True)

    if search:
        if not selected_prices:
            st.warning("Please select at least one price range.")
        else:
            now = datetime.now()
            current_day = now.strftime("%A")
            current_time = now.strftime("%H:%M")

            query = """
                SELECT DISTINCT
                    r.name,
                    r.city,
                    r.address,
                    rt.overall_rating,
                    rt.review_count,
                    p.price_level,
                    p.fork_score,
                    h.open_time,
                    h.close_time
                FROM restaurants r
                JOIN ratings rt ON r.id = rt.restaurant_id
                JOIN pricing p ON r.id = p.restaurant_id
                JOIN categories c ON r.id = c.restaurant_id
                LEFT JOIN hours h ON r.id = h.restaurant_id
                    AND h.day_of_week = %s
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
                        SELECT restaurant_id 
                        FROM hours 
                        WHERE day_of_week = %s
                        AND (
                            LPAD(SPLIT_PART(open_time, ':', 1), 2, '0') || ':' || 
                            LPAD(SPLIT_PART(open_time, ':', 2), 2, '0')
                        ) <= %s
                        AND (
                            LPAD(SPLIT_PART(close_time, ':', 1), 2, '0') || ':' || 
                            LPAD(SPLIT_PART(close_time, ':', 2), 2, '0')
                        ) >= %s
                    )
                """
                params.append(current_day)
                params.append(current_time)
                params.append(current_time)

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
            sort_by = st.radio(
                "Sort by",
                ["Fork Score", "Rating", "Review Count"],
                horizontal=True
            )

            if sort_by == "Fork Score":
                results = results.sort_values("fork_score", ascending=False)
            elif sort_by == "Rating":
                results = results.sort_values("overall_rating", ascending=False)
            else:
                results = results.sort_values("review_count", ascending=False)

            results["price_level"] = results["price_level"].map({
                1: "$",
                2: "$$",
                3: "$$$",
                4: "$$$$"
            })

            results.columns = ["Name", "City", "Address", "Rating", "Reviews", "Price", "Fork Score", "Open Time", "Close Time"]

            # surprise me buttons
            col_s1, col_s2, col_s3, col_s4 = st.columns([1, 2, 1, 1])
            with col_s2:
                if st.button("🎲 Surprise Me!", use_container_width=True):
                    top_results = results.head(20)
                    surprise = top_results.sample(1).iloc[0]
                    st.session_state.surprise = surprise
            with col_s3:
                if st.button("Reroll", use_container_width=True):
                    if len(results) > 0:
                        top_results = results.head(20)
                        surprise = top_results.sample(1).iloc[0]
                        st.session_state.surprise = surprise

            # display surprise card
            if st.session_state.get("surprise") is not None:
                surprise = st.session_state.surprise
                score = surprise["Fork Score"]
                if score >= 4.0:
                    s_color = "#2E7D32"
                    s_label = "Excellent"
                    s_emoji = "🟢"
                elif score >= 3.0:
                    s_color = "#F57F17"
                    s_label = "Great"
                    s_emoji = "🟡"
                else:
                    s_color = "#D32F2F"
                    s_label = "Good"
                    s_emoji = "🔴"

                open_fmt = format_time(surprise["Open Time"])
                close_fmt = format_time(surprise["Close Time"])
                hours_display = f"🕐 Today: {open_fmt} — {close_fmt}" if open_fmt and close_fmt else "🕐 Hours not available"

                st.markdown(f"""
                    <div style='
                        background: linear-gradient(135deg, #1A1A2E, #16213E);
                        border-radius: 16px;
                        padding: 24px;
                        margin-bottom: 24px;
                        border: 2px solid #D32F2F;
                        box-shadow: 0 0 24px rgba(211, 47, 47, 0.4);
                    '>
                        <p style='color: #D32F2F; font-size: 14px; font-weight: 700; margin: 0 0 8px 0; font-family: Poppins, sans-serif; text-transform: uppercase; letter-spacing: 2px;'>🎲 Your ForkScore Pick</p>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <div>
                                <h2 style='color: white; margin: 0; font-size: 26px; font-family: Poppins, sans-serif;'>{surprise["Name"]}</h2>
                                <p style='color: #AAAAAA; margin: 4px 0; font-size: 15px; font-family: Poppins, sans-serif;'>📍 {surprise["Address"]}, {surprise["City"]}</p>
                                <p style='color: #AAAAAA; margin: 4px 0; font-size: 15px; font-family: Poppins, sans-serif;'>⭐ {surprise["Rating"]} &nbsp;&nbsp; 💬 {int(surprise["Reviews"])} reviews &nbsp;&nbsp; 💰 {surprise["Price"]}</p>
                                <p style='color: #AAAAAA; margin: 4px 0; font-size: 13px; font-family: Poppins, sans-serif;'>{hours_display}</p>
                            </div>
                            <div style='text-align: center; min-width: 100px;'>
                                <p style='color: {s_color}; font-size: 42px; font-weight: bold; margin: 0; font-family: Poppins, sans-serif;'>{score}</p>
                                <p style='color: {s_color}; font-size: 13px; font-weight: bold; margin: 0; font-family: Poppins, sans-serif;'>{s_emoji} {s_label}</p>
                                <p style='color: #666666; font-size: 11px; margin: 0; font-family: Poppins, sans-serif;'>Fork Score</p>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            # results header
            st.markdown(f"""
                <div style='
                    background: linear-gradient(135deg, #D32F2F, #7B0000);
                    border-radius: 12px;
                    padding: 20px 24px;
                    margin-bottom: 24px;
                    text-align: center;
                '>
                    <h2 style='color: white; margin: 0; font-size: 24px; font-family: Poppins, sans-serif;'>
                        🔥 {len(results)} restaurants ranked for you in {city_display}
                    </h2>
                    <p style='color: #FFCDD2; margin: 4px 0; font-size: 14px; font-family: Poppins, sans-serif;'>
                        Sorted by Fork Score — quality and consistency, not popularity
                    </p>
                </div>
            """, unsafe_allow_html=True)

            # hover CSS
            st.markdown("""
                <style>
                .restaurant-card {
                    background-color: white;
                    border-radius: 12px;
                    padding: 20px 24px;
                    margin-bottom: 12px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                    transition: transform 0.2s ease, box-shadow 0.2s ease, border-left 0.2s ease;
                    border-left: 4px solid transparent;
                    cursor: pointer;
                }
                .restaurant-card:hover {
                    transform: translateY(-3px);
                    box-shadow: 0 8px 24px rgba(211, 47, 47, 0.3);
                    border-left: 4px solid #D32F2F;
                }
                </style>
            """, unsafe_allow_html=True)

            # restaurant cards
            for _, row in results.iterrows():
                score = row["Fork Score"]
                if score >= 4.0:
                    score_color = "#2E7D32"
                    score_label = "Excellent"
                    score_emoji = "🟢"
                elif score >= 3.0:
                    score_color = "#F57F17"
                    score_label = "Great"
                    score_emoji = "🟡"
                else:
                    score_color = "#D32F2F"
                    score_label = "Good"
                    score_emoji = "🔴"

                open_fmt = format_time(row["Open Time"])
                close_fmt = format_time(row["Close Time"])

                if open_fmt and close_fmt:
                    hours_display = f"🕐 Today: {open_fmt} — {close_fmt}"
                else:
                    hours_display = "🕐 Hours not available"

                st.markdown(f"""
                    <div class='restaurant-card'>
                        <div>
                            <h3 style='color: #1A1A1A; margin: 0; font-size: 22px; font-family: Poppins, sans-serif;'>{row["Name"]}</h3>
                            <p style='color: #666666; margin: 4px 0; font-size: 16px; font-family: Poppins, sans-serif;'>📍 {row["Address"]}, {row["City"]}</p>
                            <p style='color: #666666; margin: 4px 0; font-size: 16px; font-family: Poppins, sans-serif;'>⭐ {row["Rating"]} &nbsp;&nbsp; 💬 {int(row["Reviews"])} reviews &nbsp;&nbsp; 💰 {row["Price"]}</p>
                            <p style='color: #888888; margin: 4px 0; font-size: 14px; font-family: Poppins, sans-serif;'>{hours_display}</p>
                        </div>
                        <div style='text-align: center; min-width: 90px;'>
                            <p style='color: {score_color}; font-size: 36px; font-weight: bold; margin: 0; font-family: Poppins, sans-serif;'>{score}</p>
                            <p style='color: {score_color}; font-size: 12px; font-weight: bold; margin: 0; font-family: Poppins, sans-serif;'>{score_emoji} {score_label}</p>
                            <p style='color: #AAAAAA; font-size: 11px; margin: 0; font-family: Poppins, sans-serif;'>Fork Score</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

# ── WHAT IS FORK SCORE PAGE ───────────────────────────────────
elif st.session_state.page == "forkscore":

    # header
    col1, col2 = st.columns([1, 10])
    with col1:
        st.markdown(f"""
            <img src='data:image/png;base64,{logo_b64}' width='100'/>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div style='display: flex; flex-direction: column; justify-content: center; height: 100%;'>
                <h1 style='color: white; margin: 0; padding: 0; font-size: 48px; font-family: Poppins, sans-serif;'>ForkScore</h1>
                <p style='color: #888888; font-size: 18px; margin: 0; padding: 0; font-family: Poppins, sans-serif;'>Find Food. Score Better.</p>
            </div>
        """, unsafe_allow_html=True)

    st.divider()

    # back button
    if st.button("← Back to Search"):
        st.session_state.page = "search"
        st.rerun()

    st.markdown("""
        <style>
        .info-card {
            background-color: #1E1E1E;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 16px;
            border-left: 4px solid #D32F2F;
        }
        </style>
    """, unsafe_allow_html=True)

    # page title
    st.markdown("""
        <h2 style='color: white; font-size: 36px; font-weight: 800; font-family: Poppins, sans-serif; margin-bottom: 8px;'>
            What is the Fork Score?
        </h2>
        <p style='color: #AAAAAA; font-size: 16px; font-family: Poppins, sans-serif; margin-bottom: 32px;'>
            Every restaurant on ForkScore gets a Fork Score — a transparent, data-driven number that tells you 
            how good and how trustworthy a restaurant actually is.
        </p>
    """, unsafe_allow_html=True)

    # section 1 - the problem
    st.markdown("""
        <div class='info-card'>
            <h3 style='color: #D32F2F; font-size: 20px; font-weight: 700; margin: 0 0 12px 0; font-family: Poppins, sans-serif;'>
                The Problem with Yelp
            </h3>
            <p style='color: #CCCCCC; font-size: 15px; line-height: 1.7; margin: 0; font-family: Poppins, sans-serif;'>
                Yelp ranks restaurants by popularity, advertising spend, and user engagement — not actual quality. 
                A mediocre restaurant with 3,000 reviews consistently outranks a genuinely great one with 80 reviews.
                The algorithm is a black box. Nobody outside Yelp knows exactly why one restaurant ranks above another.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # section 2 - the formula
    st.markdown("""
        <div class='info-card'>
            <h3 style='color: #D32F2F; font-size: 20px; font-weight: 700; margin: 0 0 12px 0; font-family: Poppins, sans-serif;'>
                The Formula
            </h3>
            <p style='color: #CCCCCC; font-size: 15px; line-height: 1.7; margin: 0 0 16px 0; font-family: Poppins, sans-serif;'>
                The Fork Score combines two factors — rating and review reliability — into one transparent number. If most of the reviews are negative, then the rating would decrease,
                which also affects the Fork Score.
            </p>
            <div style='
                background: #2A2A2A;
                border-radius: 8px;
                padding: 16px 24px;
                text-align: center;
                margin-bottom: 16px;
            '>
                <p style='color: white; font-size: 22px; font-weight: 700; margin: 0; font-family: Courier New, monospace;'>
                    Fork Score = Rating × Reliability
                </p>
            </div>
            <p style='color: #CCCCCC; font-size: 15px; line-height: 1.7; margin: 0; font-family: Poppins, sans-serif;'>
                <strong style='color: white;'>Rating</strong> — the raw Yelp star rating from 1.0 to 5.0. 
                Core measure of food and experience quality.<br><br>
                <strong style='color: white;'>Reliability</strong> — a number from 0 to 1 based on how many people 
                have reviewed the restaurant. A restaurant with 8 reviews gets a reliability of 0.35. 
                One with 400 reviews gets 0.96. Restaurants with 500+ reviews are fully trusted at 1.0.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # section 3 - reliability table
    st.markdown("""
        <div class='info-card'>
            <h3 style='color: #D32F2F; font-size: 20px; font-weight: 700; margin: 0 0 16px 0; font-family: Poppins, sans-serif;'>
                Reliability by Review Count
            </h3>
    """, unsafe_allow_html=True)

    reliability_data = {
        "Reviews": ["8", "50", "150", "400", "500+"],
        "Reliability Score": ["0.35", "0.63", "0.81", "0.96", "1.00"],
        "Trust Level": ["Barely proven", "Getting reliable", "Fairly reliable", "Very reliable", "Fully trusted ✓"]
    }
    reliability_df = pd.DataFrame(reliability_data)
    st.dataframe(reliability_df, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # section 4 - why log scaling
    st.markdown("""
        <div class='info-card'>
            <h3 style='color: #D32F2F; font-size: 20px; font-weight: 700; margin: 0 0 12px 0; font-family: Poppins, sans-serif;'>
                Why Log Scaling?
            </h3>
            <p style='color: #CCCCCC; font-size: 15px; line-height: 1.7; margin: 0; font-family: Poppins, sans-serif;'>
                Trust does not grow at a constant rate as reviews accumulate. Going from 10 to 50 reviews is a 
                big deal — the restaurant is becoming proven. Going from 450 to 490 reviews barely matters — 
                it is already well established.<br><br>
                A linear formula would treat both situations identically, which is unrealistic. 
                Log scaling grows fast at first and slows down as reviews accumulate — 
                accurately reflecting how trust actually builds over time.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # section 5 - price handling
    st.markdown("""
        <div class='info-card'>
            <h3 style='color: #D32F2F; font-size: 20px; font-weight: 700; margin: 0 0 12px 0; font-family: Poppins, sans-serif;'>
                How Price Works
            </h3>
            <p style='color: #CCCCCC; font-size: 15px; line-height: 1.7; margin: 0; font-family: Poppins, sans-serif;'>
                Price is not part of the Fork Score formula. Instead you set your budget first using the price 
                filter and the Fork Score ranks every restaurant within that budget by quality and consistency. 
                This means a taco spot and a fine dining restaurant are never compared against each other 
                unless you specifically choose to include both price tiers.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # section 6 - example
    st.markdown("""
        <div class='info-card'>
            <h3 style='color: #D32F2F; font-size: 20px; font-weight: 700; margin: 0 0 16px 0; font-family: Poppins, sans-serif;'>
                Fork Score in Action
            </h3>
    """, unsafe_allow_html=True)

    example_data = {
        "Restaurant": ["Proven Taco Spot", "New Taco Spot", "Italian Bistro"],
        "Rating": ["4.5 ⭐", "4.5 ⭐", "4.7 ⭐"],
        "Reviews": ["400", "8", "300"],
        "Reliability": ["0.96", "0.35", "0.92"],
        "Fork Score": ["4.32", "1.58", "4.32"]
    }
    example_df = pd.DataFrame(example_data)
    st.dataframe(example_df, use_container_width=True, hide_index=True)

    st.markdown("""
        <p style='color: #AAAAAA; font-size: 14px; font-family: Poppins, sans-serif; margin-top: 12px;'>
            The proven taco spot and the Italian bistro tie on Fork Score even though the bistro has a 
            higher raw rating — because the taco spot has far more reviews confirming its quality. 
            The new taco spot scores much lower despite the same rating because it has not been proven yet.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # closing message
    st.markdown("""
        <div style='
            background: linear-gradient(135deg, #D32F2F, #7B0000);
            border-radius: 12px;
            padding: 24px;
            margin-top: 24px;
            text-align: center;
        '>
            <h3 style='color: white; font-size: 20px; font-weight: 700; margin: 0 0 8px 0; font-family: Poppins, sans-serif;'>
                No black box. No ads. No sponsored results.
            </h3>
            <p style='color: #FFCDD2; font-size: 15px; margin: 0; font-family: Poppins, sans-serif;'>
                Just a transparent formula that rewards quality and consistency — every time.
            </p>
        </div>
    """, unsafe_allow_html=True)