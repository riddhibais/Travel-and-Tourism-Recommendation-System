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
    .stButton>button { background-color: #e65100; color: white; border-radius: 5px; height: 3em; }
    h1 { color: #1b5e20; text-align: center; }
    .place-card { border: 1px solid #ddd; padding: 15px; border-radius: 10px; background-color: white; margin-bottom: 20px; }
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
st.sidebar.title("🍀 CG Tourism")
page = st.sidebar.selectbox("Navigation", ["Welcome", "User Input", "View Photos & Select", "Cost Estimation", "Final Travel Plan"])

# --- PAGE 1: WELCOME ---
if page == "Welcome":
    st.markdown("<h1>🙏 JAI JOHAR!</h1>", unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1623053831034-793507bc6994?auto=format&fit=crop&q=80&w=1200", use_container_width=True)
    st.markdown("""
    ### Explore the Hidden Gems of Chhattisgarh
    Our AI system helps you find the perfect destination using **Content-Based Filtering**. 
    Whether you want the waterfalls of Bastar or the Hot Springs of Balrampur, we've got you covered.
    """)

# --- PAGE 2: USER INPUT ---
elif page == "User Input":
    st.header("🎯 Set Your Preferences")
    with st.form("input_form"):
        c1, c2 = st.columns(2)
        with c1:
            # Use sorted unique values for better UX
            category = st.selectbox("Category", sorted(df['Category'].unique()))
            district = st.selectbox("District", ["Any"] + sorted(df['District'].unique().tolist()))
        with c2:
            budget = st.select_slider("Budget Range", options=["Low (0-1000)", "Mid (1000-3000)", "High (3000+)"])
            vibe = st.text_input("Vibe (e.g., Adventure, Nature, Peaceful)")
        
        if st.form_submit_button("Search"):
            st.session_state.user_prefs = {"category": category, "district": district, "vibe": vibe, "budget": budget}
            st.success(f"Preferences saved for {category}! Go to 'View Photos'.")

# --- PAGE 3: VIEW PHOTOS & SELECT ---
elif page == "View Photos & Select":
    st.header("🖼️ Recommended Places")
    if 'user_prefs' in st.session_state:
        u = st.session_state.user_prefs
        
        # --- STRICT FILTERING LOGIC ---
        # 1. Start with the full dataset
        filtered_df = df.copy()
        
        # 2. Apply Strict District Filter
        if u['district'] != "Any":
            filtered_df = filtered_df[filtered_df['District'] == u['district']]
        
        # 3. Apply Strict Category Filter
        filtered_df = filtered_df[filtered_df['Category'] == u['category']]

        # 4. Apply Budget Filter
        if u['budget'] == "Low (0-1000)":
            filtered_df = filtered_df[filtered_df['Estimated Total Trip Budget (INR) 1 Night'] <= 1000]
        elif u['budget'] == "Mid (1000-3000)":
            filtered_df = filtered_df[(filtered_df['Estimated Total Trip Budget (INR) 1 Night'] > 1000) & (filtered_df['Estimated Total Trip Budget (INR) 1 Night'] <= 3000)]
        
        if filtered_df.empty:
            st.error(f"Sorry! No places found for '{u['category']}' in '{u['district']}' within the selected budget.")
            if u['category'] == "Hot Spring":
                st.info("Note: The only Hot Spring (Tattapani) is located in Balrampur District.")
        else:
            # Use ML only to rank the filtered results
            query = f"{u['vibe']}"
            u_vec = tfidf.transform([query])
            
            # Since the matrix indices won't match our filtered_df, we re-calculate similarity manually for small subset
            # Or simpler: just display the filtered results as they are the exact matches
            st.write(f"Found {len(filtered_df)} matches:")
            
            for i, row in filtered_df.iterrows():
                with st.container():
                    st.markdown(f"<div class='place-card'>", unsafe_allow_html=True)
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        google_img = f"https://www.google.com/search?q=Chhattisgarh+{row['Place Name'].replace(' ', '+')}&tbm=isch"
                        st.markdown(f"### [📷 View Photos]({google_img})")
                    with col2:
                        st.subheader(row['Place Name'])
                        st.write(f"**District:** {row['District']}")
                        st.write(f"**Category:** {row['Category']}")
                        if st.button(f"Select {row['Place Name']}", key=f"sel_{i}"):
                            st.session_state.selected_place = row
                            st.success("Destination Locked!")
                    st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("Please fill your preferences in 'User Input' first.")

# --- PAGE 4: COST ESTIMATION ---
elif page == "Cost Estimation":
    st.header("💰 Budget Breakdown")
    if 'selected_place' in st.session_state:
        p = st.session_state.selected_place
        st.subheader(f"Pricing for: {p['Place Name']}")
        
        cost_df = pd.DataFrame({
            "Expense Category": ["Stay (1 Night)", "Food (1 Day)", "Entry Fee", "Total Estimated"],
            "Price (INR)": [f"₹{p['Avg Stay Cost per night (INR)']}", f"₹{p['Avg Food Cost per day (INR)']}", f"₹{p['Entry Fee (INR)']}", f"₹{p['Estimated Total Trip Budget (INR) 1 Night']}"]
        })
        st.table(cost_df)
    else:
        st.error("Please select a place from the 'View Photos' page first.")

# --- PAGE 5: FINAL TRAVEL PLAN ---
elif page == "Final Travel Plan":
    if 'selected_place' in st.session_state:
        p = st.session_state.selected_place
        st.header(f"🧳 Travel Guide: {p['Place Name']}")
        
        tab1, tab2, tab3 = st.tabs(["Highlights", "Transport", "Local Secrets"])
        with tab1:
            st.write(f"**Description:** {p['Notes']}")
            st.write(f"**Activities:** {p['Things to Do']}")
        with tab2:
            st.write(f"🚂 **Nearest Station:** {p['Nearest Railway Station']} ({p['Distance from Railway Station (km)']} km)")
            st.write(f"🛣️ **How to Reach:** {p['How to Reach from Raipur']}")
        with tab3:
            st.success(f"**Don't Miss Food:** {p['Local Specialty Food']}")
            st.info(f"**Shopping:** {p['Nearest Market for Shopping']}")
    else:
        st.error("Please select a destination first.")
