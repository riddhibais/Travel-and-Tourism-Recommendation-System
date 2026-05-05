import streamlit as st
import pandas as pd
import pickle
from sklearn.metrics.pairwise import cosine_similarity

# 1. Setup & Load Models
@st.cache_resource
def load_models():
    # Load your dataset
    df = pd.read_csv("CG_Tourism_Full_Updated.csv").fillna('Not Available')
    # Load the brain (PKL files) you saved in your folder
    with open('vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)
    with open('tfidf_matrix.pkl', 'rb') as f:
        matrix = pickle.load(f)
    return df, vectorizer, matrix

df, tfidf, tfidf_matrix = load_models()

# 2. Navigation Sidebar
st.sidebar.title("Travel Guide Menu")
page = st.sidebar.radio("Navigate", ["Welcome", "User Input", "Recommendations", "Cost Estimation", "Final Travel Plan"])

# --- PAGE 1: WELCOME (The Entry Point) ---
if page == "Welcome":
    st.markdown("<h1 style='text-align: center;'>🙏 Jai Johar!</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>Explore Chhattisgarh Tourism</h2>", unsafe_allow_html=True)
    
    # Visual: Chhattisgarh Map / Landscape
    # You can replace this URL with a local path to your map image if you have one
    st.image("https://incredibleindia.org/content/dam/incredible-india-v2/images/states/chhattisgarh/chhattisgarh-banner.jpg", 
             caption="The Beautiful Landscape of Chhattisgarh", use_container_width=True)
    
    st.write("---")
    st.markdown("""
    ### Welcome to the Heart of India
    Chhattisgarh is a land of **Waterfalls, Ancient Temples, and Tribal Culture**. 
    From the roaring Chitrakote Falls to the historical temples of Sirpur, there is so much to discover.
    
    **Features of this System:**
    * **ML Recommendations:** Suggests places based on your mood and vibe.
    * **Budgeting:** Estimates food and stay costs.
    * **Travel Guide:** Gives you a complete plan including things to do and local food.
    """)
    st.info("👈 Use the sidebar on the left to start your journey!")

# --- PAGE 2: USER INPUT ---
elif page == "User Input":
    st.header("🎯 What are you looking for?")
    with st.form("pref_form"):
        col1, col2 = st.columns(2)
        with col1:
            cat = st.selectbox("Select Category", options=df['Category'].unique())
            dist = st.selectbox("Select District", options=df['District'].unique())
        with col2:
            vibe = st.text_input("Describe your vibe", placeholder="e.g., quiet forest, holy temple, family picnic")
            budget = st.slider("Max Daily Budget (INR)", 500, 5000, 2000)
        
        submit = st.form_submit_button("Save My Preferences")
        if submit:
            st.session_state.user_prefs = {"category": cat, "district": dist, "vibe": vibe}
            st.success("Preferences Saved! Navigate to the 'Recommendations' page.")

# --- PAGE 3: RECOMMENDATIONS (ML LOGIC) ---
elif page == "Recommendations":
    st.header("✨ AI Recommended Destinations")
    if 'user_prefs' in st.session_state:
        u = st.session_state.user_prefs
        user_query = f"{u['category']} {u['district']} {u['vibe']}"
        
        # ML Engine
        user_vec = tfidf.transform([user_query])
        scores = cosine_similarity(user_vec, tfidf_matrix).flatten()
        top_indices = scores.argsort()[-3:][::-1]
        results = df.iloc[top_indices]
        
        for i, row in results.iterrows():
            with st.expander(f"📍 {row['Place Name']} - {row['District']}"):
                st.write(f"**Best Season:** {row['Best Season to Visit']}")
                st.write(f"**Transport:** {row['How to Reach from Raipur']}")
                if st.button(f"Select {row['Place Name']}", key=f"btn_{i}"):
                    st.session_state.selected_place = row
                    st.balloons()
                    st.success("Destination selected! Check Cost Estimation.")
    else:
        st.warning("Please enter your preferences in the 'User Input' section first.")

# --- PAGE 4: COST ESTIMATION ---
elif page == "Cost Estimation":
    st.header("💰 Budget Planner")
    if 'selected_place' in st.session_state:
        p = st.session_state.selected_place
        st.subheader(f"Estimated Costs for {p['Place Name']}")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Food/Day", f"₹{p['Avg Food Cost per day (INR)']}")
        c2.metric("Stay/Night", f"₹{p['Avg Stay Cost per night (INR)']}")
        c3.metric("Entry Fee", f"₹{p['Entry Fee (INR)']}")
        
        st.write("---")
        st.info(f"**Total Estimated Budget (1 Night):** ₹{p['Estimated Total Trip Budget (INR) 1 Night']}")
    else:
        st.error("Select a destination from the 'Recommendations' page first.")

# --- PAGE 5: FINAL TRAVEL PLAN ---
elif page == "Final Travel Plan":
    if 'selected_place' in st.session_state:
        p = st.session_state.selected_place
        st.header(f"🧳 Your Guide to {p['Place Name']}")
        
        st.subheader("📋 Travel Notes")
        st.write(p['Notes'])
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("### 🚣 Things to Do")
            st.write(p['Things to Do'])
            st.markdown("### 🍛 Local Specialty Food")
            st.write(p['Local Specialty Food'])
        with col_b:
            st.markdown("### 🛍️ Local Markets")
            st.write(p['Nearest Market for Shopping'])
            st.markdown("### 🏨 Nearby Hotels")
            st.write(p['Stay Options Near Bus Stand'])
            
        st.button("Print This Plan (Ctrl+P)")
    else:
        st.error("No destination selected. Please pick one from the 'Recommendations' page.")