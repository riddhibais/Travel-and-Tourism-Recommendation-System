# --- PAGE 2: RESULTS ---
elif st.session_state.page == 2:
    f = st.session_state.filters
    st.markdown(f"### 📍 Top Destinations in {f['cat']}")
    
    filtered = df[df['Final_Category'] == f['cat']]
    if f['dist'] != "All Chhattisgarh":
        filtered = filtered[filtered['District'] == f['dist']]
    
    # --- UPDATED BUDGET LOGIC WITH RANGES ---
    if f['budget'] == "Low": 
        filtered = filtered[filtered['Estimated Total Trip Budget (INR) 1 Night'] <= 1500]
        range_label = "Low (₹0 - ₹1,500)"
    elif f['budget'] == "Medium": 
        filtered = filtered[(filtered['Estimated Total Trip Budget (INR) 1 Night'] > 1500) & 
                            (filtered['Estimated Total Trip Budget (INR) 1 Night'] <= 4000)]
        range_label = "Medium (₹1,500 - ₹4,000)"
    else:
        filtered = filtered[filtered['Estimated Total Trip Budget (INR) 1 Night'] > 4000]
        range_label = "High (₹4,000+)"

    st.info(f"Showing results for budget range: **{range_label}**")

    if filtered.empty:
        st.warning(f"No matches found for {range_label}. Try changing the budget level or location.")
        st.button("⬅ Back to Filters", on_click=lambda: go_to(1))
    else:
        for idx, row in filtered.iterrows():
            with st.container():
                st.markdown(f"""<div class="card">
                    <span class="card-title">{row['Place Name']}</span><br>
                    <span style="color: #374151;">District: {row['District']} | Budget: ₹{row['Estimated Total Trip Budget (INR) 1 Night']}</span>
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
