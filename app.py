import streamlit as st
import pandas as pd

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
    .side-card h4 { color: #B45309 !important; font-weight: 800; margin-bottom: 5px; }
    .side-card p { color: #4B5563 !important; font-size: 0.9rem; }

    /* BUTTON TEXT FIX */
    div.stButton > button p { color: white !important; }
    .stButton>button { 
        width: 100%; border-radius: 12px; height: 3.8rem; 
        background-color: #064E3B; color: white !important; 
        font-weight: bold; font-size: 1.2rem; border: 2px solid #FCD34D;
    }
    .stButton>button:hover { background-color: #059669; border-color: #FFFFFF; }

    p, span, label, .stMarkdown { color: #1F2937 !important; font-weight: 500; }
    .card { background: #F9FAFB; padding: 25px; border-radius: 15px; border: 2px solid #E5E7EB; margin-bottom: 20px; }
    .card-title { font-size: 1.4rem; font-weight: 800; color: #064E3B !important; }
    .guide-box { background: #F0FDF4; padding: 20px; border-radius: 12px; border-left: 6px solid #059669; }
    
    /* Cost Summary Box */
    .cost-summary {
        background: #064E3B;
        color: white !important;
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        border: 4px solid #FCD34D;
    }
    .cost-summary h2, .cost-summary p { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA PROCESSING ---
@st.cache_resource
def get_clean_data():
    try:
        df = pd.read_csv("CG_Tourism_Full_Updated.csv").fillna('Not specified')
    except:
        return pd.DataFrame(columns=['Place Name', 'District', 'Category'])

    def apply_categories(row):
        name = str(row['Place Name']).lower()
        orig_cat = str(row['Category']).lower()
        if any(x in name for x in ['fall', 'chitrakoot', 'chitrakote', 'ghat', 'dhar']) or \
           any(x in orig_cat for x in ['waterfall', 'nature', 'water']): return 'Nature & Waterfalls'
        if any(x in name for x in ['sarovar', 'talab', 'lake', 'marine drive', 'riverfront', 'dam', 'reservoir']): return 'Lakes & Waterfronts'
        if any(x in name for x in ['temple', 'mandir', 'dham', 'ashram', 'church', 'mosque']) or \
           any(x in orig_cat for x in ['temple', 'religious', 'spiritual', 'pilgrimage']): return 'Religious & Spiritual'
        if any(x in name for x in ['sanctuary', 'national park', 'zoo', 'udyan', 'wildlife', 'safari', 'cave', 'gupha']) or \
           any(x in orig_cat for x in ['wildlife', 'park', 'zoo', 'cave']): return 'Wildlife & Parks'
        if any(x in name for x in ['fort', 'qila', 'palace', 'museum', 'archaeological', 'sirpur']) or \
           any(x in orig_cat for x in ['heritage', 'fort', 'archaeological', 'museum']): return 'Heritage & Culture'
        return 'Urban Leisure & Adventure'
    
    df['Final_Category'] = df.apply(apply_categories, axis=1)
    return df

df = get_clean_data()

# --- 3. NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = 0
if 'selection' not in st.session_state: st.session_state.selection = None

def go_to(idx): st.session_state.page = idx

# --- PAGE 0: FRONT PAGE ---
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
        st.markdown("""<div class="side-card"><h4>🌳 Wildlife & Heritage</h4><p>Explore National Parks and Ancient Architecture.</p></div>
                       <div class="side-card"><h4>🌊 Waterfalls</h4><p>Visit Chitrakote, Tirathgarh and more.</p></div>""", unsafe_allow_html=True)
    with col_right:
        st.markdown("""<div class="side-card"><h4>💰 Budget Tiers</h4>
                        <p><b>Low:</b> Under ₹1,500 <br> <b>Mid:</b> ₹1,500 - ₹4,000 <br> <b>High:</b> ₹4,000+</p></div>
                       <div class="side-card"><h4>🍱 Local Culture</h4><p>Authentic Bastar flavors and local festivals.</p></div>""", unsafe_allow_html=True)
    
    st.write("<br>", unsafe_allow_html=True)
    _, btn_col, _ = st.columns([1, 2, 1])
    with btn_col:
        if st.button("Start Your Journey ➔"): go_to(1)

# --- PAGE 1: PREFERENCES ---
elif st.session_state.page == 1:
    st.markdown("### 🎯 Find Your Perfect Spot")
    col1, col2 = st.columns(2)
    with col1:
        cat = st.selectbox("I want to visit:", sorted(df['Final_Category'].unique()))
        dist = st.selectbox("Location:", ["All Chhattisgarh"] + sorted(df['District'].unique().tolist()))
    with col2:
        budget_lvl = st.select_slider("Budget Level:", options=["Low", "Medium", "High"])
    
    st.session_state.filters = {"cat": cat, "dist": dist, "budget": budget_lvl}
    st.write("---")
    c1, c2 = st.columns(2)
    with c1: st.button("⬅ Back Home", on_click=lambda: go_to(0))
    with c2: st.button("Search Recommendations ➔", on_click=lambda: go_to(2))

# --- PAGE 2: RESULTS ---
elif st.session_state.page == 2:
    f = st.session_state.filters
    st.markdown(f"### 📍 Top Destinations in {f['cat']}")
    
    filtered = df[df['Final_Category'] == f['cat']]
    if f['dist'] != "All Chhattisgarh": filtered = filtered[filtered['District'] == f['dist']]
    
    if f['budget'] == "Low": filtered = filtered[filtered['Estimated Total Trip Budget (INR) 1 Night'] <= 1500]
    elif f['budget'] == "Medium": filtered = filtered[filtered['Estimated Total Trip Budget (INR) 1 Night'] <= 4000]

    if filtered.empty:
        st.warning("No matches found. Try changing the budget or location.")
        st.button("⬅ Back to Filters", on_click=lambda: go_to(1))
    else:
        for idx, row in filtered.iterrows():
            with st.container():
                st.markdown(f"""<div class="card"><span class="card-title">{row['Place Name']}</span><br>
                    <span>Location: {row['District']}</span></div>""", unsafe_allow_html=True)
                cA, cB = st.columns(2)
                with cA:
                    link = f"https://www.google.com/search?q={row['Place Name'].replace(' ', '+')}+Chhattisgarh&tbm=isch"
                    st.markdown(f"**[📷 View Photos]({link})**")
                with cB:
                    if st.button(f"View Travel Guide", key=idx):
                        st.session_state.selection = row
                        go_to(3)
                        st.rerun()

# --- PAGE 3: DETAILED GUIDE ---
elif st.session_state.page == 3:
    p = st.session_state.selection
    st.markdown(f"### 🗺️ Travel Guide: {p['Place Name']}")
    st.markdown(f"<div class='guide-box'><strong>About:</strong> {p['Notes']}</div>", unsafe_allow_html=True)
    
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("#### 🚀 How to Reach")
        st.write(f"**Route:** {p['How to Reach from Raipur']}")
        st.write(f"**Nearest Train:** {p['Nearest Railway Station']}")
    with col_r:
        st.markdown("#### 🍱 Food & Activities")
        st.write(f"**Speciality:** {p['Local Specialty Food']}")
        st.write(f"**Activities:** {p['Things to Do']}")

    st.write("---")
    c1, c2 = st.columns(2)
    with c1: st.button("⬅ Back to Results", on_click=lambda: go_to(2))
    with c2: st.button("Calculate Stay & Cost ➔", on_click=lambda: go_to(4))

# --- PAGE 4: COST ESTIMATOR ---
elif st.session_state.page == 4:
    p = st.session_state.selection
    st.markdown(f"### 💰 Trip Estimator for {p['Place Name']}")
    
    colA, colB = st.columns(2)
    with colA:
        days = st.number_input("Number of Nights Stay:", min_value=1, value=1)
        people = st.number_input("Number of Travelers:", min_value=1, value=1)
    with colB:
        stay_type = st.radio("Stay Preference:", ["Dormitory/Budget (₹500/night)", "Standard Hotel (₹1500/night)", "Luxury Resort (₹4000/night)"])
        transport = st.radio("Transport Mode:", ["Public/Bus (₹300)", "Private Cab (₹2000)", "Personal Vehicle (₹1000)"])

    # Basic Calculation Logic
    stay_cost = {"Dormitory/Budget (₹500/night)": 500, "Standard Hotel (₹1500/night)": 1500, "Luxury Resort (₹4000/night)": 4000}
    trans_cost = {"Public/Bus (₹300)": 300, "Private Cab (₹2000)": 2000, "Personal Vehicle (₹1000)": 1000}
    
    food_per_day = 500
    total_est = (stay_cost[stay_type] * days * people) + trans_cost[transport] + (food_per_day * days * people)

    st.markdown(f"""
        <div class="cost-summary">
            <p>Estimated Total Trip Cost</p>
            <h2>₹{total_est:,}</h2>
            <p>(Incl. Stay, Food, and Transport for {people} person for {days} nights)</p>
        </div>
    """, unsafe_allow_html=True)

    st.write("<br>", unsafe_allow_html=True)
    if st.button("🏠 Back to Home"): go_to(0)
