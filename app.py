import streamlit as st
import pandas as pd

# --- 1. SETTINGS & STYLING ---
st.set_page_config(page_title="CG Tourism AI", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #F4F7F6; }
    .main-title { color: #1E3A8A; text-align: center; font-weight: 800; font-size: 2.5rem; margin-bottom: 0px; }
    .sub-title { color: #64748B; text-align: center; margin-bottom: 30px; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5rem; background-color: #1E3A8A; color: white; border: none; transition: 0.3s; }
    .stButton>button:hover { background-color: #3B82F6; color: white; }
    .card { background: white; padding: 20px; border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 15px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    .price-tag { background: #DCFCE7; color: #166534; padding: 4px 10px; border-radius: 20px; font-weight: bold; font-size: 0.8rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA PROCESSING ---
@st.cache_resource
def get_clean_data():
    df = pd.read_csv("CG_Tourism_Full_Updated.csv").fillna('Information not available')
    
    def apply_categories(row):
        name = row['Place Name'].lower()
        orig_cat = row['Category']
        # Specific Correction: Lakes & Waterfronts
        if any(x in name for x in ['sarovar', 'talab', 'lake', 'marine drive', 'riverfront']): return 'Lakes & Waterfronts'
        if 'tattapani' in name: return 'Nature & Hot Springs'
        # Grouping
        if orig_cat in ['Temple', 'Religious', 'Spiritual / Pilgrimage']: return 'Religious & Spiritual'
        if orig_cat in ['Waterfall', 'Nature', 'Water Tourism']: return 'Nature & Waterfalls'
        if orig_cat in ['Wildlife', 'Park / Zoo', 'Cave']: return 'Wildlife & Parks'
        if orig_cat in ['Heritage / Fort', 'Heritage / Archaeological', 'Heritage / Urban', 'Museum / Park']: return 'Heritage & Culture'
        if orig_cat in ['Hill Station']: return 'Hill Stations'
        return 'Urban Leisure & Adventure'

    df['Final_Category'] = df.apply(apply_categories, axis=1)
    return df

df = get_clean_data()

# --- 3. SESSION STATE FOR NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = 0
if 'selection' not in st.session_state: st.session_state.selection = None

def change_page(idx): st.session_state.page = idx

# --- PAGE 0: WELCOME ---
if st.session_state.page == 0:
    st.markdown("<p class='main-title'>JAI JOHAR</p>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Chhattisgarh Tourism Intelligence System</p>", unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1623053831034-793507bc6994?w=800&q=80", use_container_width=True)
    st.write("---")
    if st.button("Start Trip Planner ➔"): change_page(1)

# --- PAGE 1: PREFERENCES ---
elif st.session_state.page == 1:
    st.markdown("### 🎯 Trip Preferences")
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            cat = st.selectbox("Interest Area", sorted(df['Final_Category'].unique()))
            dist = st.selectbox("Location", ["Chhattisgarh (All)"] + sorted(df['District'].unique().tolist()))
        with col2:
            budget_lvl = st.select_slider("Budget Level", options=["Low", "Medium", "High"])
            vibe = st.text_input("Vibe (Optional)", placeholder="e.g. Ancient, Calm")
    
    st.session_state.filters = {"cat": cat, "dist": dist, "budget": budget_lvl}
    
    st.write("---")
    c1, c2 = st.columns(2)
    with c1: st.button("⬅ Back", on_click=lambda: change_page(0))
    with c2: st.button("Find Places ➔", on_click=lambda: change_page(2))

# --- PAGE 2: SELECTION ---
elif st.session_state.page == 2:
    f = st.session_state.filters
    st.markdown(f"### 📍 Recommendations for {f['cat']}")
    
    # Logic: Inclusive Filtering
    filtered = df[df['Final_Category'] == f['cat']]
    if f['dist'] != "Chhattisgarh (All)":
        filtered = filtered[filtered['District'] == f['dist']]
    
    # Budget Logic: High includes Low and Med
    if f['budget'] == "Low":
        filtered = filtered[filtered['Estimated Total Trip Budget (INR) 1 Night'] <= 1000]
    elif f['budget'] == "Medium":
        filtered = filtered[filtered['Estimated Total Trip Budget (INR) 1 Night'] <= 3000]
    # High shows everything (no upper limit filter)

    if filtered.empty:
        st.warning("No specific matches found. Try widening your search.")
        st.button("⬅ Back to Preferences", on_click=lambda: change_page(1))
    else:
        for idx, row in filtered.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 1.2rem; font-weight: 700; color: #1E293B;">{row['Place Name']}</span>
                        <span class="price-tag">₹{row['Estimated Total Trip Budget (INR) 1 Night']}</span>
                    </div>
                    <p style="color: #64748B; margin: 5px 0;">District: {row['District']}</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Select {row['Place Name']}", key=idx):
                    st.session_state.selection = row
                    change_page(3)
                    st.rerun()
        
        st.button("⬅ Change Preferences", on_click=lambda: change_page(1))

# --- PAGE 3: SUMMARY ---
elif st.session_state.page == 3:
    p = st.session_state.selection
    st.markdown(f"### 🏁 Travel Summary: {p['Place Name']}")
    
    col1, col2 = st.columns([1.5, 1])
    with col1:
        st.info(f"**Experience:** {p['Notes']}")
        st.success(f"**Must Do:** {p['Things to Do']}")
    with col2:
        st.markdown("**💰 Cost Estimation**")
        st.write(f"Stay: ₹{p['Avg Stay Cost per night (INR)']}")
        st.write(f"Food: ₹{p['Avg Food Cost per day (INR)']}")
        st.write(f"**Total: ₹{p['Estimated Total Trip Budget (INR) 1 Night']}**")
    
    st.write("---")
    st.markdown(f"🚂 **Transport:** Nearest Station is {p['Nearest Railway Station']}.")
    st.markdown(f"🍲 **Food:** Try the local {p['Local Specialty Food']}.")
    
    st.write("---")
    c1, c2 = st.columns(2)
    with c1: st.button("⬅ Back to List", on_click=lambda: change_page(2))
    with c2: 
        if st.button("🏠 Start New Plan"):
            st.session_state.selection = None
            change_page(0)
            st.rerun()
