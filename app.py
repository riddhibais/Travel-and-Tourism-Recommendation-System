import streamlit as st
import pandas as pd
import pickle
from sklearn.metrics.pairwise import cosine_similarity

# --- 1. CONFIG & THEME ---
st.set_page_config(page_title="Chhattisgarh Tourism AI", layout="wide")

# Custom CSS for a vibrant look
st.markdown("""
    <style>
    .main { background-color: #f9fbf9; }
    .stButton>button { width: 100%; background-color: #e65100; color: white; border-radius: 5px; }
    .stButton>button:hover { background-color: #bf360c; color: white; }
    h1 { color: #1b5e20; text-shadow: 1px 1px 2px #bdbdbd; }
    .css-10trblm { color: #1b5e20; } 
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA LOAD ---
@st.cache_resource
def load_assets():
    df = pd.read_csv("CG_Tourism_Full_Updated.csv").fillna('Information not available')
    with open('vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)
    with open('tfidf_matrix.pkl', 'rb') as f:
        matrix = pickle.load(f)
    return df, vectorizer, matrix

df, tfidf, tfidf_matrix = load_assets()

# --- 3. NAVIGATION ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/Emblem_of_Chhattisgarh.svg/1200px-Emblem_of_Chhattisgarh.svg.png", width=100)
st.sidebar.title("Main Menu")
page = st.sidebar.selectbox("Navigation", ["Welcome", "User Input", "View Photos & Select", "Cost Estimation", "Final Travel Plan"])

# --- PAGE 1: WELCOME ---
if page == "Welcome":
    st.markdown("<h1 style='text-align: center;'>🙏 JAI JOHAR!</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Welcome to the Heart of India: Chhattisgarh</h3>", unsafe_allow_html=True)
    
    # Using a high-quality landscape image of Bastar/Chitrakote
    st.image("https://images.unsplash.com/photo-1623053831034-793507bc6994?auto=format&fit=crop&q=80&w=1200", 
             caption="The Majestic Chitrakote Falls", use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.success("### Why Visit?\n* 80% Forest Cover\n* Ancient Temples\n* Unique Tribal Culture")
    with col2:
        st.info("### How to use?\n1. Enter your vibe\n2. Select your budget\n3. Get your ML-powered plan")

# --- PAGE 2: USER INPUT ---
elif page == "User Input":
    st.header("🎯 Tell us your preferences")
    with st.form("input_form"):
        c1, c2 = st.columns(2)
        with c1:
            category = st.selectbox("Category", df['Category'].unique())
            district = st.selectbox("District", ["Any"] + list(df['District'].unique()))
        with c2:
            budget = st.select_slider("Budget Range", options=["Low (0-1000)", "Mid (1000-3000)", "High (3000+)"])
            vibe = st.text_input("Vibe (e.g., Adventure, Spiritual, Family)")
        
        if st.form_submit_button("Search Destinations"):
            st.session_state.user_prefs = {"category": category, "district": district, "vibe": vibe, "budget": budget}
            st.success("Search criteria saved! Proceed to 'View Photos & Select'.")

# --- PAGE 3: VIEW PHOTOS & SELECT ---
elif page == "View Photos & Select":
    st.header("🖼️ Explore Places")
    if 'user_prefs' in st.session_state:
        u = st.session_state.user_prefs
        query = f"{u['category']} {u['district']} {u['vibe']}"
        
        # ML Logic
        u_vec = tfidf.transform([query])
        scores = cosine_similarity(u_vec, tfidf_matrix).flatten()
        df['score'] = scores
        
        # Simple Budget Filter
        filtered_df = df.copy()
        if u['budget'] == "Low (0-1000)":
            filtered_df = filtered_df[filtered_df['Estimated Total Trip Budget (INR) 1 Night'] <= 1000]
        elif u['budget'] == "Mid (1000-3000)":
            filtered_df = filtered_df[(filtered_df['Estimated Total Trip Budget (INR) 1 Night'] > 1000) & (filtered_df['Estimated Total Trip Budget (INR) 1 Night'] <= 3000)]
        
        results = filtered_df.sort_values(by='score', ascending=False).head(6)
        
        # Grid Display
        cols = st.columns(2)
        for idx, (i, row) in enumerate(results.iterrows()):
            with cols[idx % 2]:
                st.subheader(row['Place Name'])
                google_img = f"https://www.google.com/search?q=Chhattisgarh+{row['Place Name'].replace(' ', '+')}&tbm=isch"
                st.markdown(f"[🔍 Click here to see Real Photos of {row['Place Name']}]({google_img})")
                st.write(f"📍 {row['District']} | ⭐ {row['Category']}")
                if st.button(f"Select {row['Place Name']}", key=f"sel_{i}"):
                    st.session_state.selected_place = row
                    st.success(f"{row['Place Name']} selected!")
    else:
        st.warning("Please fill your preferences in 'User Input' first.")

# --- PAGE 4: COST ESTIMATION ---
elif page == "Cost Estimation":
    st.header("💰 Total Trip Budget Estimation")
    if 'selected_place' in st.session_state:
        p = st.session_state.selected_place
        st.subheader(f"Pricing for: {p['Place Name']}")
        
        # Create a clean table for costs
        cost_df = pd.DataFrame({
            "Expense Category": ["Average Stay (1 Night)", "Average Food (1 Day)", "Entry Fee", "Total Estimated Cost"],
            "Price (INR)": [f"₹{p['Avg Stay Cost per night (INR)']}", f"₹{p['Avg Food Cost per day (INR)']}", f"₹{p['Entry Fee (INR)']}", f"₹{p['Estimated Total Trip Budget (INR) 1 Night']}"]
        })
        st.table(cost_df)
        
        st.info("Note: These are average prices and can vary based on season and luxury choices.")
    else:
        st.error("Please select a place from the 'View Photos' page first.")

# --- PAGE 5: FINAL TRAVEL PLAN ---
elif page == "Final Travel Plan":
    if 'selected_place' in st.session_state:
        p = st.session_state.selected_place
        st.header(f"🧳 Your Guide to {p['Place Name']}")
        
        col_main1, col_main2 = st.columns([2, 1])
        
        with col_main1:
            st.markdown("### 📝 Overview")
            st.write(p['Notes'])
            st.markdown("### 🚣 Activities")
            st.write(p['Things to Do'])
            st.markdown("### ✈️ Travel Details")
            st.write(f"**Airport:** {p['Nearest Airport']} ({p['Distance from Airport (km)']} km)")
            st.write(f"**Railway:** {p['Nearest Railway Station']} ({p['Distance from Railway Station (km)']} km)")
        
        with col_main2:
            st.markdown("### 🍛 Taste of CG")
            st.success(p['Local Specialty Food'])
            st.markdown("### 📅 Best Time")
            st.warning(p['Best Season to Visit'])
            st.markdown("### 🛍️ Shopping")
            st.info(p['Nearest Market for Shopping'])
    else:
        st.error("Please select a destination first.")
