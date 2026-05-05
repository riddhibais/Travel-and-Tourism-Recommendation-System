import streamlit as st
import pandas as pd

# --- 1. SETTINGS & ADVANCED STYLING ---
st.set_page_config(page_title="CG Tourism AI", layout="wide")

st.markdown("""
    <style>
    /* Global Background */
    .stApp { background-color: #FFFFFF; }
    
    /* Hero Section - Dark Green with White/Gold Text */
    .hero-container {
        padding: 60px 20px;
        text-align: center;
        background: linear-gradient(135deg, #064E3B 0%, #022C22 100%);
        border-radius: 25px;
        margin-bottom: 40px;
        border-bottom: 8px solid #FCD34D;
    }
    .main-title { 
        font-size: 3.5rem; 
        font-weight: 850; 
        color: #FFFFFF !important; 
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .jai-johar { 
        font-size: 2.2rem; 
        font-weight: 700; 
        color: #FCD34D !important; 
        letter-spacing: 2px;
    }
    .hero-sub {
        color: #D1FAE5 !important;
        font-size: 1.2rem;
        font-style: italic;
    }

    /* Side Info Cards for Front Page */
    .side-card {
        background: #F3F4F6;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #FCD34D;
        margin-bottom: 20px;
        text-align: center;
    }
    .side-card h4 { color: #064E3B !important; margin-bottom: 5px; }
    .side-card p { color: #4B5563 !important; font-size: 0.9rem; }

    /* Buttons */
    .stButton>button { 
        width: 100%; border-radius: 12px; height: 3.8rem; 
        background-color: #064E3B; color: white !important; 
        font-weight: bold; font-size: 1.2rem; border: 2px solid #FCD34D;
    }
    .stButton>button:hover { background-color: #059669; transform: scale(1.02); transition: 0.2s; }

    /* Other Pages Text */
    p, span, label, .stMarkdown { color: #1F2937 !important; font-weight: 500; }
    .card { background: #F9FAFB; padding: 25px; border-radius: 15px; border: 2px solid #E5E7EB; margin-bottom: 20px; }
    .guide-box { background: #F0FDF4; padding: 20px; border-radius: 12px; border-left: 6px solid #059669; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA PROCESSING ---
@st.cache_resource
def get_clean_data():
    # Make sure your CSV file is in the same folder
    try:
        df = pd.read_csv("CG_Tourism_Full_Updated.csv").fillna('Not specified')
    except:
        # Fallback if file not found
        return pd.DataFrame(columns=['Place Name', 'District', 'Category'])

    def apply_categories(row):
        name = str(row['Place Name']).lower()
        orig_cat = row['Category']
        if any(x in name for x in ['sarovar', 'talab', 'lake', 'marine drive', 'riverfront']): return 'Lakes & Waterfronts'
        if 'tattapani' in name: return 'Nature & Hot Springs'
        if orig_cat in ['Temple', 'Religious', 'Spiritual / Pilgrimage']: return 'Religious & Spiritual'
        if orig_cat in ['Waterfall', 'Nature', 'Water Tourism']: return 'Nature & Waterfalls'
        if orig_cat in ['Wildlife', 'Park / Zoo', 'Cave']: return 'Wildlife & Parks'
        if orig_cat in ['Heritage / Fort', 'Heritage / Archaeological', 'Heritage / Urban', 'Museum / Park']: return 'Heritage & Culture'
        return 'Urban Leisure & Adventure'
    
    df['Final_Category'] = df.apply(apply_categories, axis=1)
    return df

df = get_clean_data()

# --- 3. NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = 0
if 'selection' not in st.session_state: st.session_state.selection = None

def go_to(idx): st.session_state.page = idx

# --- PAGE 0: NEW ATTRACTIVE FRONT PAGE ---
if st.session_state.page == 0:
    st.markdown("""
        <div class="hero-container">
            <p class="main-title">Travel & Tourism Recommendation System</p>
            <p class="jai-johar">🌾 Jai Johar 🌾</p>
            <p class="hero-sub">Explore the Heart of India: Chhattisgarh</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 3-Column Layout to fill both sides
    col_left, col_mid, col_right = st.columns([1, 2, 1])
    
    with col_left:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
            <div class="side-card">
                <h4>🌳 Wildlife</h4>
                <p>Home to 3 National Parks and 11 Wildlife Sanctuaries.</p>
            </div>
            <div class="side-card">
                <h4>🌊 Waterfalls</h4>
                <p>Witness the majestic 'Niagara of India' - Chitrakote.</p>
            </div>
        """, unsafe_allow_html=True)

    with col_mid:
        st.markdown("<h4 style='text-align:center;'>📍 CG Destination Map</h4>", unsafe_allow_html=True)
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Chhattisgarh_map.png/400px-Chhattisgarh_map.png", use_container_width=True)
        st.write("<br>", unsafe_allow_html=True)
        if st.button("Start Your Journey ➔"): go_to(1)

    with col_right:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
            <div class="side-card">
                <h4>🛕 Heritage</h4>
                <p>Ancient temples and archaeological wonders of Sirpur.</p>
            </div>
            <div class="side-card">
                <h4>🍱 Culture</h4>
                <p>Taste the unique flavors of Bastar and Raipur.</p>
            </div>
        """, unsafe_allow_html=True)

# --- PAGE 1: PREFERENCES ---
elif st.session_state.page == 1:
    st.markdown("### 🎯 Find Your Perfect Spot")
    col1, col2 = st.columns(2)
    with col1:
        cat = st.selectbox("I want to visit:", sorted(df['Final_Category'].unique()))
        dist = st.selectbox("Location:", ["All Chhattisgarh"] + sorted(df['District'].unique().tolist()))
    with col2:
        budget_lvl = st.select_slider("Budget Level:", options=["Low", "Medium", "High"])
        st.write("<br>", unsafe_allow_html=True)
    
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
    if f['dist'] != "All Chhattisgarh":
        filtered = filtered[filtered['District'] == f['dist']]
    
    if f['budget'] == "Low": filtered = filtered[filtered['Estimated Total Trip Budget (INR) 1 Night'] <= 1000]
    elif f['budget'] == "Medium": filtered = filtered[filtered['Estimated Total Trip Budget (INR) 1 Night'] <= 3000]

    if filtered.empty:
        st.warning("No matches found. Try selecting 'All Chhattisgarh' for more results.")
        st.button("⬅ Back to Filters", on_click=lambda: go_to(1))
    else:
        for idx, row in filtered.iterrows():
            with st.container():
                st.markdown(f"""<div class="card">
                    <span style="font-size: 1.4rem; font-weight: 800; color: #064E3B !important;">{row['Place Name']}</span><br>
                    <span style="color: #374151;">District: {row['District']} | Budget: ₹{row['Estimated Total Trip Budget (INR) 1 Night']}</span>
                </div>""", unsafe_allow_html=True)
                
                cA, cB = st.columns(2)
                with cA:
                    link = f"https://www.google.com/search?q={row['Place Name'].replace(' ', '+')}+Chhattisgarh&tbm=isch"
                    st.markdown(f"**[📷 Click to View Photos]({link})**")
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
        st.write(f"**Nearest Train:** {p['Nearest Railway Station']} ({p['Distance from Railway Station (km)']} km)")
        st.write(f"**Nearest Airport:** {p['Nearest Airport']}")
        st.markdown("#### 🍱 Food & Markets")
        st.write(f"**Speciality:** {p['Local Specialty Food']}")

    with col_r:
        st.markdown("#### 🚣 Activities")
        st.write(p['Things to Do'])
        
        if p['Final_Category'] in ['Nature & Waterfalls', 'Wildlife & Parks']:
            st.markdown("#### 🛡️ Seasonal Safety (Nature/Forest)")
            st.write(f"**Best Time:** {p['Best Season to Visit']}")
            st.info(f"**Monsoon Status:** {p['Safe to Visit in Monsoon']}")
        
        st.markdown("#### 💰 Costs")
        st.write(f"**Total Budget:** ₹{p['Estimated Total Trip Budget (INR) 1 Night']}")

    st.write("---")
    if st.button("🏠 Plan Another Trip"):
        st.session_state.selection = None
        go_to(0)
        st.rerun()
