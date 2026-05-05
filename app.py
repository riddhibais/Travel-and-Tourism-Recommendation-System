import streamlit as st
import pandas as pd
import pickle
from sklearn.metrics.pairwise import cosine_similarity

# --- 1. SET THEME & COLORS ---
st.set_page_config(page_title="Chhattisgarh Tourism AI", layout="wide")

# Custom CSS for a colorful look (Green & Gold Theme)
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { background-color: #2e7d32; color: white; border-radius: 10px; }
    .stMetric { background-color: #ffffff; padding: 10px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    h1 { color: #e65100; }
    h2 { color: #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOAD DATA & MODELS ---
@st.cache_resource
def load_assets():
    df = pd.read_csv("CG_Tourism_Full_Updated.csv").fillna('Not Available')
    with open('vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)
    with open('tfidf_matrix.pkl', 'rb') as f:
        matrix = pickle.load(f)
    return df, vectorizer, matrix

df, tfidf, tfidf_matrix = load_assets()

# --- 3. SIDEBAR NAVIGATION ---
st.sidebar.title("🏝️ CG Explorer")
page = st.sidebar.radio("Go to:", ["Welcome", "User Input", "Recommendations", "Cost Estimation", "Final Travel Plan"])

# --- PAGE 1: WELCOME ---
if page == "Welcome":
    st.markdown("<h1 style='text-align: center;'>🙏 Jai Johar!</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Welcome to the Heart of Incredible India</h3>", unsafe_allow_html=True)
    
    # Chhattisgarh Map Image Placeholder
    st.image("https://www.chhattisgarhtourism.org/images/cg-map.png", width=400) # Use a direct URL to a map
    
    st.write("---")
    st.write("Chhattisgarh is known for its waterfalls, temples, and forests. This AI system uses **Machine Learning** to find the best spots for you based on your budget and vibe.")

# --- PAGE 2: USER INPUT ---
elif page == "User Input":
    st.header("🎯 Define Your Trip")
    with st.form("user_form"):
        col1, col2 = st.columns(2)
        with col1:
            cat = st.selectbox("I want to visit:", df['Category'].unique())
            dist = st.selectbox("Preferred District:", ["Any"] + list(df['District'].unique()))
        with col2:
            budget_range = st.select_slider("Select Budget Range (INR)", 
                                            options=["Low (0-1000)", "Mid (1000-3000)", "High (3000+)"])
            vibe = st.text_input("Vibe", placeholder="e.g. peaceful, waterfall, ancient history")
            
        if st.form_submit_button("Find My Places"):
            st.session_state.user_prefs = {
                "category": cat, 
                "district": "" if dist == "Any" else dist, 
                "vibe": vibe,
                "budget": budget_range
            }
            st.success("Preferences saved! Go to Recommendations.")

# --- PAGE 3: RECOMMENDATIONS ---
elif page == "Recommendations":
    st.header("✨ Places Filtered for You")
    if 'user_prefs' in st.session_state:
        u = st.session_state.user_prefs
        
        # 1. Machine Learning Search
        query = f"{u['category']} {u['district']} {u['vibe']}"
        u_vec = tfidf.transform([query])
        scores = cosine_similarity(u_vec, tfidf_matrix).flatten()
        
        # 2. Add scores to DF and filter by Budget Range
        df_copy = df.copy()
        df_copy['score'] = scores
        
        # Budget Filtering Logic
        if u['budget'] == "Low (0-1000)":
            df_copy = df_copy[df_copy['Estimated Total Trip Budget (INR) 1 Night'] <= 1000]
        elif u['budget'] == "Mid (1000-3000)":
            df_copy = df_copy[(df_copy['Estimated Total Trip Budget (INR) 1 Night'] > 1000) & (df_copy['Estimated Total Trip Budget (INR) 1 Night'] <= 3000)]
        else:
            df_copy = df_copy[df_copy['Estimated Total Trip Budget (INR) 1 Night'] > 3000]

        top_results = df_copy.sort_values(by='score', ascending=False).head(4)

        if top_results.empty:
            st.warning("No places found in this budget. Try a higher budget range!")
        else:
            for i, row in top_results.iterrows():
                with st.container():
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        # Since we don't have images in CSV, we show a colored box with Category
                        st.info(f"📁 {row['Category']}")
                    with c2:
                        st.subheader(row['Place Name'])
                        st.write(f"📍 **District:** {row['District']}")
                        st.write(f"💰 **Estimated Cost:** ₹{row['Estimated Total Trip Budget (INR) 1 Night']}")
                        if st.button(f"Choose {row['Place Name']}", key=i):
                            st.session_state.selected_place = row
                            st.success(f"Selected {row['Place Name']}!")
                    st.divider()
    else:
        st.warning("Please go to User Input first.")

# --- PAGE 4: COST ESTIMATION ---
elif page == "Cost Estimation":
    if 'selected_place' in st.session_state:
        p = st.session_state.selected_place
        st.header(f"💰 Budget Breakdown for {p['Place Name']}")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Stay (per night)", f"₹{p['Avg Stay Cost per night (INR)']}")
        col2.metric("Food (per day)", f"₹{p['Avg Food Cost per day (INR)']}")
        col3.metric("Entry Fee", f"₹{p['Entry Fee (INR)']}")
        
        st.markdown(f"### Total Trip Estimate: **₹{p['Estimated Total Trip Budget (INR) 1 Night']}**")
    else:
        st.error("Select a place from Recommendations first.")

# --- PAGE 5: FINAL TRAVEL PLAN ---
elif page == "Final Travel Plan":
    if 'selected_place' in st.session_state:
        p = st.session_state.selected_place
        st.title(f"🗺️ Destination: {p['Place Name']}")
        
        tab1, tab2, tab3 = st.tabs(["Overview", "How to Reach", "Tips"])
        
        with tab1:
            st.write(f"**Things to do:** {p['Things to Do']}")
            st.write(f"**Local Food to try:** {p['Local Specialty Food']}")
            st.write(f"**Suitable for:** {p['Suitable For']}")
            # Link to images
            google_url = f"https://www.google.com/search?q=Chhattisgarh+Tourism+{p['Place Name'].replace(' ', '+')}&tbm=isch"
            st.markdown(f"[📷 View Photos of {p['Place Name']}]({google_url})", unsafe_allow_html=True)
        
        with tab2:
            st.write(f"✈️ **Airport:** {p['Nearest Airport']} ({p['Distance from Airport (km)']} km)")
            st.write(f"🚂 **Railway:** {p['Nearest Railway Station']} ({p['Distance from Railway Station (km)']} km)")
            st.write(f"🛣️ **Route:** {p['How to Reach from Raipur']}")
            
        with tab3:
            st.write(f"📅 **Best Season:** {p['Best Season to Visit']}")
            st.write(f"📝 **Notes:** {p['Notes']}")
    else:
        st.error("Please pick a destination first.")
