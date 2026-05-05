import streamlit as st
import pandas as pd
import pickle
from sklearn.metrics.pairwise import cosine_similarity

# --- 1. CONFIG & THEME ---
st.set_page_config(page_title="Chhattisgarh Tourism AI", layout="wide")

# --- 2. DATA LOAD & CLEANING ---
@st.cache_resource
def load_assets():
    df = pd.read_csv("CG_Tourism_Full_Updated.csv").fillna('Information not available')
    
    # --- SIMPLIFY CATEGORIES ---
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

# --- 3. NAVIGATION ---
st.sidebar.title("🍀 CG Tourism")
page = st.sidebar.selectbox("Navigation", ["Welcome", "User Input", "View Photos & Select", "Cost Estimation", "Final Travel Plan"])

# Page 1: Welcome (Keep your previous code for Welcome)
if page == "Welcome":
    st.markdown("<h1 style='text-align: center;'>🙏 JAI JOHAR!</h1>", unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1623053831034-793507bc6994?auto=format&fit=crop&q=80&w=1200", use_container_width=True)
    st.markdown("### Search 50+ Hidden Gems using our Smart ML Engine")

# Page 2: User Input
elif page == "User Input":
    st.header("🎯 Set Your Preferences")
    with st.form("input_form"):
        c1, c2 = st.columns(2)
        with c1:
            # Now using the simplified categories!
            category = st.selectbox("I am interested in:", sorted(df['Simplified_Category'].unique()))
            district = st.selectbox("Select District:", ["Any"] + sorted(df['District'].unique().tolist()))
        with c2:
            budget = st.select_slider("Budget Range", options=["Low (0-1000)", "Mid (1000-3000)", "High (3000+)"])
            vibe = st.text_input("Vibe (e.g. peaceful, trek, ancient)")
        
        if st.form_submit_button("Search"):
            st.session_state.user_prefs = {"category": category, "district": district, "vibe": vibe, "budget": budget}
            st.success(f"Preferences saved! Go to 'View Photos'.")

# Page 3: View Photos & Select
elif page == "View Photos & Select":
    st.header("🖼️ Recommended Places")
    if 'user_prefs' in st.session_state:
        u = st.session_state.user_prefs
        
        # --- STRICT FILTERING ---
        filtered_df = df.copy()
        
        # 1. District Filter
        if u['district'] != "Any":
            filtered_df = filtered_df[filtered_df['District'] == u['district']]
        
        # 2. Category Filter (Using Simplified Column)
        filtered_df = filtered_df[filtered_df['Simplified_Category'] == u['category']]

        # 3. Budget Filter
        if u['budget'] == "Low (0-1000)":
            filtered_df = filtered_df[filtered_df['Estimated Total Trip Budget (INR) 1 Night'] <= 1000]
        elif u['budget'] == "Mid (1000-3000)":
            filtered_df = filtered_df[(filtered_df['Estimated Total Trip Budget (INR) 1 Night'] > 1000) & (filtered_df['Estimated Total Trip Budget (INR) 1 Night'] <= 3000)]
        elif u['budget'] == "High (3000+)":
            filtered_df = filtered_df[filtered_df['Estimated Total Trip Budget (INR) 1 Night'] > 3000]
        
        if filtered_df.empty:
            st.error(f"No matches found in {u['district']} for this selection. Try a broader search!")
        else:
            st.write(f"✅ Found {len(filtered_df)} matches:")
            for i, row in filtered_df.iterrows():
                with st.expander(f"📍 {row['Place Name']} ({row['District']})"):
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.markdown(f"**[📷 View Photos](https://www.google.com/search?q=Chhattisgarh+{row['Place Name'].replace(' ', '+')}&tbm=isch)**")
                    with col2:
                        st.write(f"Original Category: {row['Category']}")
                        if st.button(f"Select {row['Place Name']}", key=f"sel_{i}"):
                            st.session_state.selected_place = row
                            st.success("Destination Saved!")
    else:
        st.warning("Please fill your preferences in 'User Input' first.")

# Page 4 & 5: (Keep your existing code for Cost and Final Plan)
# ... [rest of the code] ...
