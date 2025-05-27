import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.title("🪐 Dune Character Explorer")

# --- Data Loading ---
@st.cache_data
def load_data():
    # Adjust path if needed
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'duneCharacters_kaggle.csv')
    # Set encoding as per your previous step!
    df = pd.read_csv(data_path, encoding='latin1')
    return df

df = load_data()

# --- Sidebar Filter ---
st.sidebar.header("Filter by Book")
books = ['All'] + sorted(df['Book'].dropna().unique())
selected_book = st.sidebar.selectbox("Book", books)

if selected_book != 'All':
    filtered_df = df[df['Book'] == selected_book]
else:
    filtered_df = df

# --- Bar Chart: Characters per House ---
house_counts = filtered_df['House_Allegiance'].value_counts().reset_index()
house_counts.columns = ['House_Allegiance', 'Count']

fig = px.bar(
    house_counts,
    x='House_Allegiance',
    y='Count',
    color='House_Allegiance',
    title="Number of Characters per House",
    labels={'House_Allegiance': 'House', 'Count': 'Number of Characters'},
)

fig.update_layout(showlegend=False, xaxis={'categoryorder':'total descending'})

st.plotly_chart(fig, use_container_width=True)
