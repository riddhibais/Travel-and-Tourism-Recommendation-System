import streamlit as st
import pandas as pd
import pickle
from sklearn.metrics.pairwise import cosine_similarity

# --- 1. CONFIG & THEME ---
st.set_page_config(page_title="Chhattisgarh Tourism AI", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f9fbf9; }
    .stButton>button { border-radius: 20px; height: 3em; font-weight: bold; }
    .next-btn>button { background-color: #e65100; color: white; }
    .back-btn>button { background-color: #757575; color: white; }
    h1 { color: #1b5e20; text-align: center; }
    .place-card { border: 1px solid #ddd; padding: 20px; border-radius: 15px; background-color: white; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA LOAD & CLEANING ---
@st.cache_resource
def load_assets():
    df = pd.read_csv("CG_Tourism_Full_Updated.csv").fillna('Information not available')
    
    # Category Grouping Logic
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
    
    with open('vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)
    with open('tfidf_matrix.pkl', 'rb') as f:
        matrix = pickle.load(f)
    return df, vectorizer, matrix

df, tfidf, tfidf_matrix = load_assets()

# --- 3. NAVIGATION STATE MANAGEMENT ---
if 'step' not in st.session_state:
    st.session_state.step = 0

def next_step(): st.session_state.step += 1
def prev_step(): st.session_state.step -= 1

steps = ["Welcome", "User Input", "View Photos & Select", "Cost Estimation", "Final Travel Plan"]

# --- PAGE 0: WELCOME ---
if st.session_state.step == 0:
    st.markdown("<h1>🙏 JAI JOHAR!</h1>", unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1623053831034-793507bc6994?auto=format&fit=crop&q=80&w=1200", use_container_width=True)
    st.markdown("<h3 style='text-align: center;'>Explore 50+ Hidden Gems of Chhattisgarh</h3>", unsafe_allow_html=True)
    st.write("---")
    st.info("Welcome to the AI Travel Planner. We will help you find the perfect destination based on your vibe and budget.")
    
    c1, c2, c3 = st.columns([4, 2, 4])
    with c2:
        st.button("Start Planning ➡️", on_click=next_step)

# --- PAGE 1: USER INPUT ---
elif st.session_state.step == 1:
    st.header("🎯 Step 1: Set Your Preferences")
    col1, col2 = st.columns(2)
    with col1:
        category = st.selectbox("I am interested in:", sorted(df['Simplified_Category'].unique()))
        district = st.selectbox("Select District:", ["Any"] + sorted(df['District'].unique().tolist()))
    with col2:
        budget = st.select_slider("Budget Range", options=["Low (0-1000)", "Mid (1000-3000)", "High (3000+)"])
        vibe = st.text_input("Vibe (e.g. peaceful, adventure, history)")
    
    st.session_state.user_prefs = {"category": category, "district": district, "vibe": vibe, "budget": budget}
    
    st.write("---")
    b1, b2, b3 = st.columns([2, 6, 2])
    with b1: st.button("⬅️ Back", on_click=prev_step)
    with b3: st.button("Next ➡️", on_click=next_step)

# --- PAGE 2: VIEW PHOTOS & SELECT ---
elif st.session_state.step == 2:
    st.header("🖼️ Step 2: Explore & Select")
    u = st.session_state.get('user_prefs', {})
    
    # Filtering Logic
    f_df = df.copy()
    if u.get('district') != "Any":
        f_df = f_df[f_df['District'] == u['district']]
    
    f_df = f_df[f_df['Simplified_Category'] == u.get('category')]

    # Improved Budget Logic
    if u.get('budget') == "Low (0-1000)":
        f_df = f_df[f_df['Estimated Total Trip Budget (INR) 1 Night'] <= 1000]
    elif u.get('budget') == "Mid (1000-3000)":
        f_df = f_df[f_df['Estimated Total Trip Budget (INR) 1 Night'] <= 3000]
    
    if f_df.empty:
        st.error("No matches found! Try changing the District or Budget.")
        st.button("⬅️ Back to Preferences", on_click=prev_step)
    else:
        for i, row in f_df.iterrows():
            with st.container():
                st.markdown(f"<div class='place-card'>", unsafe_allow_html=True)
                c1, c2 = st.columns([1, 2])
                with c1:
                    google_img = f"https://www.google.com/search?q=Chhattisgarh+{row['Place Name'].replace(' ', '+')}&tbm=isch"
                    st.markdown(f"### [📷 View Photos]({google_img})")
                with c2:
                    st.subheader(row['Place Name'])
                    st.write(f"**District:** {row['District']} | **Cost:** ₹{row['Estimated Total Trip Budget (INR) 1 Night']}")
                    if st.button(f"Select {row['Place Name']}", key=f"sel_{i}"):
                        st.session_state.selected_place = row
                        st.success(f"Selected {row['Place Name']}! Click Next to see budget.")
                st.markdown("</div>", unsafe_allow_html=True)
        
        st.write("---")
        b1, b2, b3 = st.columns([2, 6, 2])
        with b1: st.button("⬅️ Back", on_click=prev_step)
        if 'selected_place' in st.session_state:
            with b3: st.button("Next ➡️", on_click=next_step)

# --- PAGE 3: COST ESTIMATION ---
elif st.session_state.step == 3:
    st.header("💰 Step 3: Cost Estimation")
    p = st.session_state.get('selected_place')
    if p is not None:
        st.subheader(f"Pricing Breakdown for {p['Place Name']}")
        cost_df = pd.DataFrame({
            "Expense Category": ["Stay (1 Night)", "Food (1 Day)", "Entry Fee", "Total Estimated"],
            "Price (INR)": [f"₹{p['Avg Stay Cost per night (INR)']}", f"₹{p['Avg Food Cost per day (INR)']}", f"₹{p['Entry Fee (INR)']}", f"₹{p['Estimated Total Trip Budget (INR) 1 Night']}"]
        })
        st.table(cost_df)
    
    st.write("---")
    b1, b2, b3 = st.columns([2, 6, 2])
    with b1: st.button("⬅️ Back", on_click=prev_step)
    with b3: st.button("Next ➡️", on_click=next_step)

# --- PAGE 4: FINAL PLAN ---
elif st.session_state.step == 4:
    p = st.session_state.get('selected_place')
    st.header(f"🧳 Final Step: Your Travel Plan for {p['Place Name']}")
    
    t1, t2 = st.columns([2, 1])
    with t1:
        st.markdown("### 📝 About")
        st.write(p['Notes'])
        st.markdown("### 🚣 Activities")
        st.write(p['Things to Do'])
    with t2:
        st.markdown("### 🍛 Local Specialty")
        st.success(p['Local Specialty Food'])
        st.markdown("### 🚂 Nearest Station")
        st.info(p['Nearest Railway Station'])

    st.write("---")
    st.button("⬅️ Back to Costs", on_click=prev_step)
    if st.button("🏠 Start Over"):
        st.session_state.step = 0
        st.rerun()
