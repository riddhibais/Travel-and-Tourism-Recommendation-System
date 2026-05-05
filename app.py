import streamlit as st
import pandas as pd
import pickle

# --- 1. CONFIG & THEME ---
st.set_page_config(page_title="Chhattisgarh Tourism AI", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f9fbf9; }
    .stButton>button { border-radius: 20px; height: 3em; font-weight: bold; width: 100%; }
    .next-btn>button { background-color: #e65100; color: white; }
    .back-btn>button { background-color: #757575; color: white; }
    h1 { color: #1b5e20; text-align: center; }
    .place-card { 
        border: 2px solid #e0e0e0; 
        padding: 20px; 
        border-radius: 15px; 
        background-color: white; 
        margin-bottom: 20px; 
        box-shadow: 2px 4px 8px rgba(0,0,0,0.1);
    }
    .selected-card {
        border: 2px solid #2e7d32;
        background-color: #f1f8e9;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA LOAD & CLEANING ---
@st.cache_resource
def load_assets():
    df = pd.read_csv("CG_Tourism_Full_Updated.csv").fillna('Not available')
    
    category_map = {
        'Temple': 'Religious & Spiritual', 'Religious': 'Religious & Spiritual', 'Spiritual / Pilgrimage': 'Religious & Spiritual',
        'Waterfall': 'Nature & Waterfalls', 'Nature': 'Nature & Waterfalls', 'Water Tourism': 'Nature & Waterfalls', 
        'Hot Spring': 'Nature & Waterfalls', 'Lake / River': 'Nature & Waterfalls', 'Lake / Dam': 'Nature & Waterfalls',
        'Heritage / Fort': 'Heritage & Culture', 'Heritage / Archaeological': 'Heritage & Culture', 
        'Heritage / Urban': 'Heritage & Culture', 'Tribal / Cultural': 'Heritage & Culture', 'Museum / Park': 'Heritage & Culture',
        'Wildlife': 'Wildlife & Parks', 'Park / Zoo': 'Wildlife & Parks', 'Cave': 'Wildlife & Parks',
        'Hill Station': 'Hill Stations',
        'Urban Attraction': 'Leisure & Lifestyle', 'Shopping / Food Market': 'Leisure & Lifestyle', 
        'Leisure/Nature': 'Leisure & Lifestyle', 'Adventure': 'Leisure & Lifestyle'
    }
    df['Simplified_Category'] = df['Category'].map(category_map)
    return df

df = load_assets()

# --- 3. NAVIGATION STATE ---
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'selected_place' not in st.session_state:
    st.session_state.selected_place = None

def next_step(): st.session_state.step += 1
def prev_step(): st.session_state.step -= 1

# --- PAGE 0: WELCOME ---
if st.session_state.step == 0:
    st.markdown("<h1>🙏 JAI JOHAR!</h1>", unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1623053831034-793507bc6994?auto=format&fit=crop&q=80&w=1200", use_container_width=True)
    st.markdown("<h3 style='text-align: center;'>CG Tourism Smart AI Planner</h3>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([4, 2, 4])
    with c2: st.button("Start Planning ➡️", on_click=next_step)

# --- PAGE 1: USER INPUT ---
elif st.session_state.step == 1:
    st.header("🎯 Step 1: Search Preferences")
    col1, col2 = st.columns(2)
    with col1:
        category = st.selectbox("I am interested in:", sorted(df['Simplified_Category'].unique()))
        district = st.selectbox("Select District:", ["Any"] + sorted(df['District'].unique().tolist()))
    with col2:
        budget = st.select_slider("Budget Range", options=["Low (0-1000)", "Mid (1000-3000)", "High (3000+)"])
        vibe = st.text_input("Vibe (e.g. peaceful, adventure)")
    
    st.session_state.user_prefs = {"category": category, "district": district, "vibe": vibe, "budget": budget}
    
    st.write("---")
    b1, b2, b3 = st.columns([2, 6, 2])
    with b1: st.button("⬅️ Back", on_click=prev_step)
    with b3: st.button("Next ➡️", on_click=next_step)

# --- PAGE 2: VIEW PHOTOS & SELECT ---
elif st.session_state.step == 2:
    st.header("🖼️ Step 2: Select a Destination")
    u = st.session_state.get('user_prefs', {})
    
    # Filter Data
    f_df = df.copy()
    if u.get('district') != "Any":
        f_df = f_df[f_df['District'] == u['district']]
    f_df = f_df[f_df['Simplified_Category'] == u.get('category')]

    # Budget logic (Low shows Low, Mid shows Mid + Low)
    if u.get('budget') == "Low (0-1000)":
        f_df = f_df[f_df['Estimated Total Trip Budget (INR) 1 Night'] <= 1000]
    elif u.get('budget') == "Mid (1000-3000)":
        f_df = f_df[f_df['Estimated Total Trip Budget (INR) 1 Night'] <= 3000]

    if f_df.empty:
        st.error("No places match your search. Try changing the District or Budget!")
        st.button("⬅️ Change Preferences", on_click=prev_step)
    else:
        st.write(f"Showing {len(f_df)} results in {u['district']}:")
        for i, row in f_df.iterrows():
            # Check if this place is already selected
            is_selected = st.session_state.selected_place is not None and st.session_state.selected_place['Place Name'] == row['Place Name']
            card_class = "place-card selected-card" if is_selected else "place-card"
            
            st.markdown(f"<div class='{card_class}'>", unsafe_allow_html=True)
            c1, c2 = st.columns([1, 2])
            with c1:
                st.write(f"### [📷 View Photos](https://www.google.com/search?q=Chhattisgarh+{row['Place Name'].replace(' ', '+')}&tbm=isch)")
                st.write(f"💰 Budget: ₹{row['Estimated Total Trip Budget (INR) 1 Night']}")
            with c2:
                st.subheader(row['Place Name'])
                st.write(f"📍 District: {row['District']}")
                if st.button(f"✅ Click to Select {row['Place Name']}", key=f"btn_{i}"):
                    st.session_state.selected_place = row
                    st.rerun() # Refresh to show selection
            st.markdown("</div>", unsafe_allow_html=True)

        st.write("---")
        b1, b2, b3 = st.columns([2, 6, 2])
        with b1: st.button("⬅️ Back", on_click=prev_step)
        if st.session_state.selected_place is not None:
            with b3: st.button("Next ➡️", on_click=next_step)
        else:
            with b3: st.info("Select a place to continue")

# --- PAGE 3: COST ESTIMATION ---
elif st.session_state.step == 3:
    st.header("💰 Step 3: Trip Cost")
    p = st.session_state.selected_place
    
    st.success(f"Estimated Budget for {p['Place Name']}")
    cost_data = {
        "Item": ["Stay (1 Night)", "Food (1 Day)", "Entry Fees", "Total"],
        "Cost": [f"₹{p['Avg Stay Cost per night (INR)']}", f"₹{p['Avg Food Cost per day (INR)']}", f"₹{p['Entry Fee (INR)']}", f"₹{p['Estimated Total Trip Budget (INR) 1 Night']}"]
    }
    st.table(pd.DataFrame(cost_data))
    
    st.write("---")
    b1, b2, b3 = st.columns([2, 6, 2])
    with b1: st.button("⬅️ Back", on_click=prev_step)
    with b3: st.button("Next ➡️", on_click=next_step)

# --- PAGE 4: FINAL TRAVEL PLAN ---
elif st.session_state.step == 4:
    p = st.session_state.selected_place
    st.header(f"🧳 Final Travel Guide: {p['Place Name']}")
    
    colA, colB = st.columns([2, 1])
    with colA:
        st.markdown("### 📝 Highlights")
        st.write(p['Notes'])
        st.markdown("### 🚣 Activities")
        st.write(p['Things to Do'])
    with colB:
        st.info(f"**District:** {p['District']}")
        st.success(f"**Local Food:** {p['Local Specialty Food']}")
        st.warning(f"**Transport:** Nearest Station - {p['Nearest Railway Station']}")

    st.write("---")
    if st.button("🏠 Plan Another Trip"):
        st.session_state.step = 0
        st.session_state.selected_place = None
        st.rerun()
