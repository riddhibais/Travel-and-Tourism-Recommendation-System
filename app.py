import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- 1. SETTINGS & ADVANCED STYLING ---
st.set_page_config(page_title="CG Tourism AI", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .hero-container {
        padding: 60px 20px;
        text-align: center;
        background: linear-gradient(135deg, #064E3B 0%, #022C22 100%);
        border-radius: 25px;
        margin-bottom: 40px;
        border-bottom: 8px solid #FCD34D;
    }
    .hero-container .main-title { 
        font-size: 3.5rem; 
        font-weight: 850; 
        color: #FFFFFF !important; 
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .hero-container .jai-johar { 
        font-size: 2.2rem; 
        font-weight: 700; 
        color: #FCD34D !important; 
        letter-spacing: 2px;
    }
    .hero-container .hero-sub {
        color: #FFFFFF !important;
        font-size: 1.2rem;
        font-style: italic;
    }
    .side-card {
        background: #F3F4F6;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #FCD34D;
        margin-bottom: 20px;
        text-align: center;
    }
    .side-card h4 { 
        color: #B45309 !important; 
        font-weight: 800;
        margin-bottom: 5px; 
    }
    .side-card p { color: #4B5563 !important; font-size: 0.9rem; }

    div.stButton > button p { color: white !important; }
    .stButton>button { 
        width: 100%; border-radius: 12px; height: 3.8rem; 
        background-color: #064E3B; 
        color: white !important; 
        font-weight: bold; font-size: 1.2rem; border: 2px solid #FCD34D;
    }
    .stButton>button:hover { background-color: #059669; border-color: #FFFFFF; }

    p, span, label, .stMarkdown { color: #1F2937 !important; font-weight: 500; }
    .card { background: #F9FAFB; padding: 25px; border-radius: 15px; border: 2px solid #E5E7EB; margin-bottom: 20px; }
    .card-title { font-size: 1.4rem; font-weight: 800; color: #064E3B !important; }
    .guide-box { background: #F0FDF4; padding: 20px; border-radius: 12px; border-left: 6px solid #059669; }
    
    .rec-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #ddd;
        text-align: center;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA PROCESSING & ML ENGINE ---
@st.cache_resource
def get_clean_data():
    try:
        df = pd.read_csv("CG_Tourism_Full_Updated.csv").fillna('Not specified')
    except:
        return pd.DataFrame(columns=['Place Name', 'District', 'Category', 'Estimated Total Trip Budget (INR) 1 Night'])

    def apply_categories(row):
        name = str(row['Place Name']).lower()
        orig_cat = str(row['Category']).lower()
        if any(x in name for x in ['fall', 'chitrakoot', 'chitrakote', 'ghat', 'dhar']) or \
           any(x in orig_cat for x in ['waterfall', 'nature', 'water']):
            return 'Nature & Waterfalls'
        if any(x in name for x in ['sarovar', 'talab', 'lake', 'marine drive', 'riverfront', 'dam', 'reservoir']):
            return 'Lakes & Waterfronts'
        if any(x in name for x in ['temple', 'mandir', 'dham', 'ashram', 'church', 'mosque']) or \
           any(x in orig_cat for x in ['temple', 'religious', 'spiritual', 'pilgrimage']):
            return 'Religious & Spiritual'
        if any(x in name for x in ['sanctuary', 'national park', 'zoo', 'udyan', 'wildlife', 'safari', 'cave', 'gupha']) or \
           any(x in orig_cat for x in ['wildlife', 'park', 'zoo', 'cave']):
            return 'Wildlife & Parks'
        if any(x in name for x in ['fort', 'qila', 'palace', 'museum', 'archaeological', 'sirpur']) or \
           any(x in orig_cat for x in ['heritage', 'fort', 'archaeological', 'museum']):
            return 'Heritage & Culture'
        return 'Urban Leisure & Adventure'
    
    df['Final_Category'] = df.apply(apply_categories, axis=1)
    return df

df = get_clean_data()

def get_ml_recommendations(place_name, full_df):
    full_df['combined_features'] = full_df['Final_Category'] + " " + full_df['District'] + " " + full_df['Notes']
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(full_df['combined_features'])
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    try:
        idx = full_df.index[full_df['Place Name'] == place_name][0]
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_indices = [i[0] for i in sim_scores[1:4]]
        return full_df.iloc[sim_indices]
    except:
        return pd.DataFrame()

# --- 3. NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = 0
if 'selection' not in st.session_state: st.session_state.selection = None

def go_to(idx): st.session_state.page = idx

# PAGE 0: FRONT PAGE
if st.session_state.page == 0:
    st.markdown("""
        <div class="hero-container">
            <p class="main-title">Travel & Tourism Recommendation System</p>
            <p class="jai-johar">🌾 Jai Johar 🌾</p>
            <p class="hero-sub">Welcome to Chhattisgarh — the land of golden grains and warm hearts.</p>
        </div>
    """, unsafe_allow_html=True)
    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("""<div class="side-card"><h4>🌳 Wildlife</h4><p>Home to 3 National Parks and 11 Wildlife Sanctuaries.</p></div>
                       <div class="side-card"><h4>🌊 Waterfalls</h4><p>Witness the majestic 'Niagara of India' - Chitrakote.</p></div>""", unsafe_allow_html=True)
    with col_right:
        st.markdown("""<div class="side-card"><h4>🛕 Heritage</h4><p>Ancient temples and archaeological wonders of Sirpur.</p></div>
                       <div class="side-card"><h4>🍱 Culture</h4><p>Taste the unique flavors of Bastar and Raipur.</p></div>""", unsafe_allow_html=True)
    st.write("<br>", unsafe_allow_html=True)
    _, btn_col, _ = st.columns([1, 2, 1])
    with btn_col:
        if st.button("Start Your Journey ➔"): go_to(1)

# PAGE 1: PREFERENCES
elif st.session_state.page == 1:
    st.markdown("### 🎯 Find Your Perfect Spot")
    col1, col2 = st.columns(2)
    with col1:
        cat_options = ["All Categories"] + sorted(df['Final_Category'].unique().tolist())
        cat = st.selectbox("I want to visit:", cat_options)
        dist = st.selectbox("Location:", ["All Chhattisgarh"] + sorted(df['District'].unique().tolist()))
    with col2:
        budget_lvl = st.select_slider("Budget Level (for 1 Night):", options=["Low (0-1500)", "Medium (1500-3000)", "High (3000+)"])
    st.session_state.filters = {"cat": cat, "dist": dist, "budget": budget_lvl}
    st.write("---")
    c1, c2 = st.columns(2)
    with c1: st.button("⬅ Back Home", on_click=lambda: go_to(0))
    with c2: st.button("Search Recommendations ➔", on_click=lambda: go_to(2))

# PAGE 2: RESULTS
elif st.session_state.page == 2:
    f = st.session_state.filters
    st.markdown(f"### 📍 Recommended Destinations")
    filtered = df.copy()
    if f['cat'] != "All Categories": filtered = filtered[filtered['Final_Category'] == f['cat']]
    if f['dist'] != "All Chhattisgarh": filtered = filtered[filtered['District'] == f['dist']]
    if "Low" in f['budget']: filtered = filtered[filtered['Estimated Total Trip Budget (INR) 1 Night'] <= 1500]
    elif "Medium" in f['budget']: filtered = filtered[filtered['Estimated Total Trip Budget (INR) 1 Night'] <= 3000]
    if filtered.empty:
        st.warning("No matches found. Try expanding your budget or location.")
        st.button("⬅ Back to Filters", on_click=lambda: go_to(1))
    else:
        st.info(f"Showing {len(filtered)} destinations.")
        for idx, row in filtered.iterrows():
            with st.container():
                st.markdown(f'<div class="card"><span class="card-title">{row["Place Name"]}</span><br><span style="color: #374151;">District: {row["District"]} | Category: {row["Final_Category"]}</span></div>', unsafe_allow_html=True)
                cA, cB = st.columns(2)
                with cA:
                    link = f"https://www.google.com/search?q={row['Place Name'].replace(' ', '+')}+Chhattisgarh&tbm=isch"
                    st.markdown(f"**[📷 View Photos]({link})**")
                with cB:
                    if st.button(f"View Travel Guide", key=idx):
                        st.session_state.selection = row
                        go_to(3)
                        st.rerun()

# PAGE 3: DETAILED GUIDE + ML SECTION
elif st.session_state.page == 3:
    p = st.session_state.selection
    st.markdown(f"### 🗺️ Travel Guide: {p['Place Name']}")
    st.markdown(f"<div class='guide-box'><strong>About:</strong> {p['Notes']}</div>", unsafe_allow_html=True)
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("#### 🚀 How to Reach")
        st.write(f"**Route (from Raipur):** {p['How to Reach from Raipur']}")
        st.write(f"**Nearest station:** {p['Nearest Railway Station']}")
    with col_r:
        st.markdown("#### 🍱 Food & Activities")
        st.write(f"**Food Speciality:** {p['Local Specialty Food']}")
        st.write(f"**Things to Do:** {p['Things to Do']}")
    st.markdown("---")
    st.markdown("#### 🤖 AI Recommendations (People also visited)")
    ml_recs = get_ml_recommendations(p['Place Name'], df)
    if not ml_recs.empty:
        cols = st.columns(3)
        for i, (m_idx, m_row) in enumerate(ml_recs.iterrows()):
            with cols[i]:
                st.markdown(f'<div class="rec-card"><b>{m_row["Place Name"]}</b><br><small>{m_row["District"]}</small></div>', unsafe_allow_html=True)
                if st.button("Explore", key=f"ml_{m_idx}"):
                    st.session_state.selection = m_row
                    st.rerun()
    st.write("---")
    c1, c2 = st.columns(2)
    with c1: st.button("⬅ Back to Results", on_click=lambda: go_to(2))
    with c2: st.button("💰 View Budget Estimator ➔", on_click=lambda: go_to(4))

# PAGE 4: UPDATED BUDGET INFORMATION
elif st.session_state.page == 4:
    st.markdown("### 📊 Average Cost Information")
    st.markdown("""
    <div class="card">
        <h4 style='color:#064E3B'>🏠 Stay (Accommodation)</h4>
        <ul>
            <li><b>Budget Guesthouses:</b> ₹500 - ₹800 per night</li>
            <li><b>Standard Hotels / CTB Resorts:</b> ₹1,200 - ₹2,500 per night</li>
            <li><b>Luxury / Heritage Stays:</b> ₹4,000+ per night</li>
        </ul>
    </div>
    <div class="card">
        <h4 style='color:#064E3B'>🍱 Food & Dining (Daily Avg)</h4>
        <ul>
            <li><b>Street Food / Local Dhaba:</b> ₹150 - ₹300 per day</li>
            <li><b>Mid-range Restaurants:</b> ₹400 - ₹800 per day</li>
            <li><b>Speciality Meals (Bastar Thali etc.):</b> ₹500+ per meal</li>
        </ul>
    </div>
    <div class="card">
        <h4 style='color:#064E3B'>🚗 Travel & Transport</h4>
        <ul>
            <li><b>Public Bus / Shared Auto:</b> ₹50 - ₹200 for local spots</li>
            <li><b>Private Taxi:</b> ₹12 - ₹15 per km (Minimum 250km/day usually)</li>
            <li><b>Bike Rentals:</b> ₹400 - ₹600 per day (in cities like Raipur/Jagdalpur)</li>
        </ul>
    </div>
    <div class="guide-box">
        <b>💡 Total Average Budget:</b> A comfortable trip usually costs between <b>₹1,500 to ₹3,000 per person/day</b> excluding major long-distance travel.
    </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    if st.button("🏠 Start New Search"):
        st.session_state.selection = None
        go_to(0)
        st.rerun()
