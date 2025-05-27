import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Dune Character Explorer", layout="wide")
st.title("🪐 Dune Character Explorer")
st.write(
    """
    Explore Frank Herbert's Dune universe: visualize characters by House, Culture, and more!
    """
)

# --- Data Loading ---
@st.cache_data
def load_data():
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'duneCharacters_kaggle.csv')
    df = pd.read_csv(data_path)
    return df

df = load_data()

# --- Summary Stats ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Characters", len(df))
col2.metric("Unique Houses", df['House_Allegiance'].nunique())
col3.metric("Unique Cultures", df['Culture'].nunique())
col4.metric("Books", df['Book'].nunique())

st.markdown("---")

# --- Sidebar Filters ---
st.sidebar.header("🔎 Filter Characters")
books = ['All'] + sorted(df['Book'].dropna().unique())
selected_book = st.sidebar.selectbox("Book", books)

if selected_book != 'All':
    filtered_df = df[df['Book'] == selected_book]
else:
    filtered_df = df

# --- Bar Chart: Characters per House ---
house_counts = (
    filtered_df['House_Allegiance']
    .fillna('Unknown')
    .value_counts()
    .reset_index()
    .rename(columns={'index': 'House_Allegiance', 'House_Allegiance': 'Count'})
)

fig = px.bar(
    house_counts,
    x='House_Allegiance', y='Count',
    title="Number of Characters per House",
    labels={'House_Allegiance': 'House', 'Count': 'Number of Characters'},
    color='House_Allegiance'
)
fig.update_layout(showlegend=False, xaxis={'categoryorder':'total descending'})
st.plotly_chart(fig, use_container_width=True)

# --- Bar Chart: Characters per Culture ---
culture_counts = (
    filtered_df['Culture']
    .fillna('Unknown')
    .value_counts()
    .head(10)
    .reset_index()
    .rename(columns={'index': 'Culture', 'Culture': 'Count'})
)

fig_culture = px.bar(
    culture_counts,
    x='Culture', y='Count',
    title="Top 10 Cultures by Number of Characters",
    labels={'Culture': 'Culture', 'Count': 'Number of Characters'},
    color='Culture'
)
fig_culture.update_layout(showlegend=False, xaxis={'categoryorder':'total descending'})
st.plotly_chart(fig_culture, use_container_width=True)

st.markdown("---")

# --- Character Detail Viewer ---
st.subheader("Character Explorer")
# Optional: allow user to filter by House/Culture as well
houses = ['All'] + sorted(df['House_Allegiance'].dropna().unique())
selected_house = st.selectbox("Select House", houses)
if selected_house != 'All':
    char_df = filtered_df[filtered_df['House_Allegiance'] == selected_house]
else:
    char_df = filtered_df

names = sorted(char_df['Character'].dropna().unique())
selected_char = st.selectbox("Select Character", names)
char_info = char_df[char_df['Character'] == selected_char].iloc[0]

with st.expander(f"Details for {selected_char}", expanded=True):
    st.markdown(f"**House:** {char_info['House_Allegiance']}")
    st.markdown(f"**Culture:** {char_info['Culture']}")
    st.markdown(f"**Book:** {char_info['Book']}")
    st.markdown(f"**Born:** {char_info['Born']}")
    st.markdown(f"**Died:** {char_info['Died']}")
    st.markdown(f"**Description:** {char_info['Detail']}")
    st.markdown(f"[Wiki link]({char_info['URL']})" if pd.notnull(char_info['URL']) else "")

# --- Ready for future features ---
# To add: Relationship network, timelines, more filters...

