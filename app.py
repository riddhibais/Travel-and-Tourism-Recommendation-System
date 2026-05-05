import streamlit as st
import pandas as pd

# --- 1. SETTINGS & HIGH-CONTRAST STYLING ---
st.set_page_config(page_title="CG Tourism AI", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .main-title { color: #064E3B; text-align: center; font-weight: 800; font-size: 2.8rem; margin-bottom: 0px; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5rem; background-color: #064E3B; color: white; font-weight: bold; }
    .stButton>button:hover { background-color: #059669; border: 2px solid #064E3B; }
    /* Ensure text is always dark and visible */
    p, span, label { color: #1F2937 !important; font-weight: 500; }
    .card { background: #F3F4F6; padding: 20px; border-radius: 15px; border: 2px solid #E5E7EB; margin-bottom: 15px; }
    .guide-box { background: #ECFDF5; padding: 20px; border-radius: 12px; border-left: 5px solid #059669; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA PROCESSING ---
@st.cache_resource
def get_clean_data():
    df = pd.read_csv("CG_Tourism_Full_Updated.csv").fillna('Not specified')
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

# --- 3. STEP-BY-STEP NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = 0
if 'selection' not in st.session_state: st.session_state.selection = None

def go_to(idx): st.session_state.page = idx

# --- PAGE 0: WELCOME ---
if st.session_state.page == 0:
    st.markdown("<p class='main-title'>JAI JOHAR</p>", unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1623053831034-793507bc6994?w=1000&q=80", use_container_width=True)
    st.write("---")
    st.markdown("<h3 style='text-align:center;'>Welcome to Chhattisgarh's Smartest Travel Guide</h3>", unsafe_allow_html=True)
    if st.button("Start My Journey ➔"): go_to(1)

# --- PAGE 1: FILTERS ---
elif st.session_state.page == 1:
    st.markdown("### 🎯 Preferences")
    col1, col2 = st.columns(2)
    with col1:
        cat = st.selectbox("What do you want to see?", sorted(df['Final_Category'].unique()))
        dist = st.selectbox("Which district?", ["All Chhattisgarh"] + sorted(df['District'].unique().tolist()))
    with col2:
        budget_lvl = st.select_slider("Budget Comfort", options=["Low", "Medium", "High"])
        vibe = st.text_input("Vibe (Optional)", placeholder="e.g. peaceful, trek")
    
    st.session_state.filters = {"cat": cat, "dist": dist, "budget": budget_lvl}
    
    st.write("---")
    c1, c2 = st.columns(2)
    with c1: st.button("⬅ Back", on_click=lambda: go_to(0))
    with c2: st.button("Find Matching Places ➔", on_click=lambda: go_to(2))

# --- PAGE 2: SELECTION & IMAGES ---
elif st.session_state.page == 2:
    f = st.session_state.filters
    st.markdown(f"### 📍 Recommended for you in {f['cat']}")
    
    filtered = df[df['Final_Category'] == f['cat']]
    if f['dist'] != "All Chhattisgarh":
        filtered = filtered[filtered['District'] == f['dist']]
    
    if f['budget'] == "Low": filtered = filtered[filtered['Estimated Total Trip Budget (INR) 1 Night'] <= 1000]
    elif f['budget'] == "Medium": filtered = filtered[filtered['Estimated Total Trip Budget (INR) 1 Night'] <= 3000]

    if filtered.empty:
        st.warning("No matches found for this specific budget/district. Try 'All Chhattisgarh'.")
        st.button("⬅ Adjust Search", on_click=lambda: go_to(1))
    else:
        for idx, row in filtered.iterrows():
            with st.container():
                st.markdown(f"""<div class="card">
                    <span style="font-size: 1.3rem; font-weight: 700;">{row['Place Name']}</span><br>
                    <span style="color: #064E3B;">📍 {row['District']} | 💰 Budget: ₹{row['Estimated Total Trip Budget (INR) 1 Night']}</span>
                </div>""", unsafe_allow_html=True)
                
                colA, colB = st.columns(2)
                with colA:
                    img_url = f"https://www.google.com/search?q=Chhattisgarh+{row['Place Name'].replace(' ', '+')}&tbm=isch"
                    st.markdown(f"**[🖼️ View Photos of {row['Place Name']}]({img_url})**")
                with colB:
                    if st.button(f"Select & View Details", key=idx):
                        st.session_state.selection = row
                        go_to(3)
                        st.rerun()

# --- PAGE 3: COST BREAKDOWN ---
elif st.session_state.page == 3:
    p = st.session_state.selection
    st.markdown(f"### 💰 Budget for {p['Place Name']}")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Avg Stay", f"₹{p['Avg Stay Cost per night (INR)']}")
    c2.metric("Avg Food", f"₹{p['Avg Food Cost per day (INR)']}")
    c3.metric("Entry Fee", f"₹{p['Entry Fee (INR)']}")
    
    st.success(f"**Total Estimated Trip (1 Night): ₹{p['Estimated Total Trip Budget (INR) 1 Night']}**")
    st.write("---")
    
    col_x, col_y = st.columns(2)
    with col_x: st.button("⬅ Back to Results", on_click=lambda: go_to(2))
    with col_y: st.button("Generate Detailed Guide ➔", on_click=lambda: go_to(4))

# --- PAGE 4: THE ULTIMATE GUIDE (EVERYTHING ELSE) ---
elif st.session_state.page == 4:
    p = st.session_state.selection
    st.markdown(f"### 🗺️ Full Destination Guide: {p['Place Name']}")
    
    st.markdown(f"<div class='guide-box'><strong>Overview:</strong> {p['Notes']}</div>", unsafe_allow_html=True)
    
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("#### 🚣 Things To Do")
        st.write(p['Things to Do'])
        st.markdown("#### 🚆 Logistics & Transport")
        st.write(f"**From Raipur:** {p['How to Reach from Raipur']}")
        st.write(f"**Station:** {p['Nearest Railway Station']} ({p['Distance from Railway Station (km)']} km)")
        st.write(f"**Airport:** {p['Nearest Airport']} ({p['Distance from Airport (km)']} km)")
    
    with col_r:
        st.markdown("#### 🍲 Food & Shopping")
        st.write(f"**Local Speciality:** {p['Local Specialty Food']}")
        st.write(f"**Market:** {p['Nearest Market for Shopping']}")
        st.markdown("#### 📅 Seasonal Safety")
        st.write(f"**Best Time:** {p['Best Season to Visit']}")
        st.write(f"**Winter Safe?** {p['Safe to Visit in Winter']}")
        st.write(f"**Monsoon Safe?** {p['Safe to Visit in Monsoon']}")

    st.write("---")
    if st.button("🏠 Start New Plan"):
        st.session_state.selection = None
        go_to(0)
        st.rerun()
