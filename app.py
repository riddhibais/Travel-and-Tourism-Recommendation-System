import streamlit as st
import pandas as pd
import pickle
from sklearn.metrics.pairwise import cosine_similarity

# --- 1. SETTINGS ---
st.set_page_config(page_title="CG Tourism AI", layout="wide")

# --- LOAD ML ---
@st.cache_resource
def load_ml():
    with open("vectorizer.pkl", "rb") as f:
        tfidf = pickle.load(f)
    with open("tfidf_matrix.pkl", "rb") as f:
        tfidf_matrix = pickle.load(f)
    return tfidf, tfidf_matrix

tfidf, tfidf_matrix = load_ml()

# --- DATA ---
@st.cache_resource
def get_clean_data():
    df = pd.read_csv("CG_Tourism_Full_Updated.csv").fillna('')

    def apply_categories(row):
        name = str(row['Place Name']).lower()
        orig_cat = str(row['Category']).lower()
        if any(x in name for x in ['fall','chitrakote']) or any(x in orig_cat for x in ['water']):
            return 'Nature & Waterfalls'
        if any(x in name for x in ['temple','mandir']) or any(x in orig_cat for x in ['religious']):
            return 'Religious & Spiritual'
        return 'Other'

    df['Final_Category'] = df.apply(apply_categories, axis=1)

    # 🔥 IMPORTANT (ML ke liye)
    df['features'] = df['Category'] + " " + df['District'] + " " + df['Sub-Category'] + " " + df['Things to Do']

    return df

df = get_clean_data()

# --- NAV ---
if 'page' not in st.session_state: st.session_state.page = 0
if 'selection' not in st.session_state: st.session_state.selection = None

def go_to(x): st.session_state.page = x

# --- PAGE 1 ---
if st.session_state.page == 0:
    st.title("🌾 CG Tourism ML System")
    if st.button("Start"): go_to(1)

# --- PAGE 2: RESULTS ---
elif st.session_state.page == 2:
    import pickle
    from sklearn.metrics.pairwise import cosine_similarity

    f = st.session_state.filters
    st.markdown(f"### 📍 Recommended Destinations")
    
    # 🔹 Load ML (safe load inside page)
    with open("vectorizer.pkl", "rb") as f1:
        tfidf = pickle.load(f1)
    with open("tfidf_matrix.pkl", "rb") as f2:
        tfidf_matrix = pickle.load(f2)

    # 🔹 STEP 1: SAME FILTER (no change)
    filtered = df.copy()

    if f['cat'] != "All Categories":
        filtered = filtered[filtered['Final_Category'] == f['cat']]
        
    if f['dist'] != "All Chhattisgarh":
        filtered = filtered[filtered['District'] == f['dist']]
    
    if "Low" in f['budget']:
        filtered = filtered[filtered['Estimated Total Trip Budget (INR) 1 Night'] <= 1500]
    elif "Medium" in f['budget']:
        filtered = filtered[filtered['Estimated Total Trip Budget (INR) 1 Night'] <= 3000]

    # 🔴 अगर filter से कुछ नहीं मिला
    if filtered.empty:
        st.warning("No matches found for this filter. Try expanding your budget or location.")
        st.button("⬅ Back to Filters", on_click=lambda: go_to(1))

    else:
        # 🔹 STEP 2: ML SORTING (not replacing, just improving order)
        
        # features ensure
        filtered['features'] = filtered['Category'] + " " + filtered['District'] + " " + filtered['Sub-Category'] + " " + filtered['Things to Do']
        
        user_text = f['cat'] + " " + f['dist'] + " travel tourism"
        user_vec = tfidf.transform([user_text])

        filtered_vec = tfidf.transform(filtered['features'])

        similarity = cosine_similarity(user_vec, filtered_vec)

        # sort by similarity
        filtered['score'] = similarity[0]
        filtered = filtered.sort_values(by='score', ascending=False)

        # 🔹 LIMIT RESULTS
        filtered = filtered.head(10)

        st.info(f"Showing {len(filtered)} smart recommendations (ML Ranked)")

        # 🔹 SAME UI DISPLAY (NO CHANGE)
        for idx, row in filtered.iterrows():
            with st.container():
                st.markdown(f"""<div class="card">
                    <span class="card-title">{row['Place Name']}</span><br>
                    <span style="color: #374151;">District: {row['District']} | Category: {row['Final_Category']}</span>
                </div>""", unsafe_allow_html=True)
                
                cA, cB = st.columns(2)
                with cA:
                    link = f"https://www.google.com/search?q={row['Place Name'].replace(' ', '+')}+Chhattisgarh&tbm=isch"
                    st.markdown(f"**[📷 View Photos]({link})**")
                with cB:
                    if st.button(f"View Travel Guide", key=idx):
                        st.session_state.selection = row
                        go_to(3)
                        st.rerun()

# --- PAGE 3 RESULT (ML HERE) ---
elif st.session_state.page == 2:
    f = st.session_state.filters

    # 🔥 ML START
    user_text = f['cat'] + " " + f['dist']
    user_vec = tfidf.transform([user_text])
    similarity = cosine_similarity(user_vec, tfidf_matrix)

    indices = similarity.argsort()[0][::-1]
    recommended = df.iloc[indices]
    # 🔥 ML END

    # OPTIONAL FILTER
    if f['cat'] != "All":
        recommended = recommended[recommended['Final_Category'] == f['cat']]

    if f['dist'] != "All":
        recommended = recommended[recommended['District'] == f['dist']]

    recommended = recommended.head(5)

    if recommended.empty:
        st.warning("No result")
    else:
        for i, row in recommended.iterrows():
            st.markdown(f"### 📍 {row['Place Name']}")
            st.write(f"District: {row['District']}")
            st.write(f"Things: {row['Things to Do']}")
            st.write("---")
