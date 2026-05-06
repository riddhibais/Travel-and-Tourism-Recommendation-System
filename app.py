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

# --- PAGE 2 INPUT ---
elif st.session_state.page == 1:
    cat = st.selectbox("Category", ["All"] + df['Final_Category'].unique().tolist())
    dist = st.selectbox("District", ["All"] + df['District'].unique().tolist())

    st.session_state.filters = {"cat": cat, "dist": dist}

    if st.button("Search"): go_to(2)

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
