import streamlit as st
import pandas as pd
import plotly.express as px
import os
import time

st.set_page_config(page_title="Dune Character Explorer", layout="wide")

# --- Banner Image ---
st.markdown(
    """
    <style>
    .banner-img {
        width: 100%;
        max-height: 250px;
        object-fit: cover;
        border-radius: 12px;
        margin-bottom: 0.7rem;
        box-shadow: 0 2px 16px rgba(0,0,0,0.25);
    }
    </style>
    """,
    unsafe_allow_html=True
)

data_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'dune_banner.png')

st.title("🪐 Dune Character Explorer")
st.markdown("> Visualize the universe of Frank Herbert’s Dune — characters, houses, relationships, and more.")
st.image(data_path ,  use_container_width=True)


print("Streamlit script started:", time.time())

# --- Data Loading ---
@st.cache_data
def load_data():
    print("Loading data...")
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'duneCharacters_kaggle.csv')
    df = pd.read_csv(data_path, encoding="latin1")
    return df
df = load_data()

# --- Summary Stats ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Characters", df['Character'].nunique())
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

DUNE_HOUSE_COLORS = {
    'Atreides': '#145A32',
    'Harkonnen': '#232b2b',
    'Corrino': '#B7950B',
    'Ordos': '#2980B9',
    'Richese': '#884EA0',
    'Vernius': '#DC7633',
    'Fenring': '#A569BD',
    'Ecaz': '#C0392B',
    'Moritani': '#566573',
    'Camatra': '#2874A6',
    'Unknown': '#CCCCCC'
}

unique_chars = filtered_df.drop_duplicates(subset=["Character"])

house_counts = (
    unique_chars['House_Allegiance']
    .fillna('Unknown')
    .value_counts()
    .reset_index()
    .rename(columns={'index': 'House_Allegiance', 'count': 'Count'})
)

fig = px.bar(
    house_counts,
    x='House_Allegiance', y='Count',
    title="Number of Characters per House",
    labels={'House_Allegiance': 'House', 'Count': 'Number of Characters'},
    color='House_Allegiance',
    color_discrete_map=DUNE_HOUSE_COLORS 
)
fig.update_layout(showlegend=False, xaxis={'categoryorder':'total descending'})

st.plotly_chart(fig, use_container_width=True)

# --- Timeline ---

st.markdown("## 📅 Character Lifespan Timeline")

timeline_df = df.copy()
timeline_df = timeline_df[pd.to_numeric(timeline_df['Born'], errors='coerce').notnull()]
timeline_df['Born'] = pd.to_numeric(timeline_df['Born'], errors='coerce')
timeline_df['Died'] = pd.to_numeric(timeline_df['Died'], errors='coerce')
timeline_df['Died'] = timeline_df['Died'].fillna(timeline_df['Born'] + 1)
timeline_df['Lifespan'] = timeline_df['Died'] - timeline_df['Born']
timeline_df = timeline_df.sort_values('Born')
timeline_df = timeline_df.drop_duplicates(subset=['Character'])

DUNE_HOUSE_COLORS = {
    'Atreides': '#145A32',
    'Harkonnen': '#232b2b',
    'Corrino': '#B7950B',
    'Ordos': '#2980B9',
    'Richese': '#884EA0',
    'Vernius': '#DC7633',
    'Fenring': '#A569BD',
    'Ecaz': '#C0392B',
    'Moritani': '#566573',
    'Camatra': '#2874A6',
    'Unknown': '#CCCCCC'
}

timeline_df['House_Color'] = timeline_df['House_Allegiance'].map(DUNE_HOUSE_COLORS).fillna('#CCCCCC')

fig = px.bar(
    timeline_df,
    y='Character',
    x='Lifespan',
    base='Born',
    color='House_Allegiance',
    orientation='h',
    color_discrete_map=DUNE_HOUSE_COLORS,
    title="Dune Character Lifespans",
    custom_data=['Born', 'Died', 'Lifespan', 'House_Allegiance', 'Book']
)
fig.update_traces(
    hovertemplate=(
        "Character: %{y}<br>"
        "Born: %{customdata[0]}<br>"
        "Died: %{customdata[1]}<br>"
        "Lifespan: %{customdata[2]} years<br>"
        "House: %{customdata[3]}<br>"
        "Book: %{customdata[4]}<extra></extra>"
    )
)
fig.update_layout(
    yaxis=dict(autorange='reversed'),
    xaxis_title="Year"
)

st.plotly_chart(fig, use_container_width=True)

# --- Character Detail Viewer ---
st.subheader("Character Explorer")

# Filter by House/Culture as well
houses = ['All'] + sorted(df['House_Allegiance'].dropna().unique())
selected_house = st.selectbox("Select House", houses)
if selected_house != 'All':
    char_df = filtered_df[filtered_df['House_Allegiance'] == selected_house]
else:
    char_df = filtered_df

names = sorted(char_df['Character'].dropna().unique())
selected_char = st.selectbox("Select Character", names)
char_info = char_df[char_df['Character'] == selected_char].iloc[0]

# Compute lifespan if Born and Died are available
try:
    born = float(char_info['Born'])
    died = float(char_info['Died'])
    lifespan = int(died - born) if pd.notnull(born) and pd.notnull(died) else None
except Exception:
    lifespan = None

with st.expander(f"Details for {selected_char}", expanded=True):
    st.markdown(f"**House:** {char_info['House_Allegiance']}")
    st.markdown(f"**Culture:** {char_info['Culture']}")
    st.markdown(f"**Book:** {char_info['Book']}")
    st.markdown(f"**Born:** {char_info['Born']}")
    st.markdown(f"**Died:** {char_info['Died']}")
    if lifespan is not None:
        st.markdown(f"**Lifespan:** {lifespan} years")
    st.markdown(f"**Description:** {char_info['Detail']}")
    st.markdown(f"[Wiki link]({char_info['URL']})" if pd.notnull(char_info['URL']) else "")


# --- Relationships ---
import networkx as nx
import plotly.graph_objects as go

st.markdown("## Character Relationship Network")

# --- Inline Filters for the Network ---
houses = ['All'] + sorted([h for h in df['House_Allegiance'].dropna().unique() if h])
books = ['All'] + sorted([b for b in df['Book'].dropna().unique() if b])
relationship_types = ['All'] + sorted([r for r in df['relationship_type'].dropna().unique() if r])

col1, col2, col3 = st.columns(3)
with col1:
    selected_house = st.selectbox("Filter by House", houses, key="rel_house")
with col2:
    selected_book = st.selectbox("Filter by Book", books, key="rel_book")
with col3:
    selected_rel = st.selectbox("Relationship type", relationship_types, key="rel_type")


# --- Filter relationship data ---
rel_df = df.dropna(subset=['to'])
rel_df = rel_df[rel_df['Character'] != rel_df['to']]
if selected_house != 'All':
    rel_df = rel_df[rel_df['House_Allegiance'] == selected_house]
if selected_book != 'All':
    rel_df = rel_df[rel_df['Book'] == selected_book]
if selected_rel != 'All':
    rel_df = rel_df[rel_df['relationship_type'] == selected_rel]

MAX_EDGES = 50
if rel_df.shape[0] > MAX_EDGES:
    rel_df = rel_df.sample(MAX_EDGES, random_state=1)

G = nx.from_pandas_edgelist(
    rel_df,
    source='Character',
    target='to',
    edge_attr='relationship_type',
    create_using=nx.DiGraph()
)

# House color mapping (use your DUNE_HOUSE_COLORS dict)
DUNE_HOUSE_COLORS = {
    'Atreides': '#145A32',
    'Harkonnen': '#232b2b',
    'Corrino': '#B7950B',
    'Ordos': '#2980B9',
    'Richese': '#884EA0',
    'Vernius': '#DC7633',
    'Fenring': '#A569BD',
    'Ecaz': '#C0392B',
    'Moritani': '#566573',
    'Camatra': '#2874A6',
    'Unknown': '#CCCCCC'
}
node_colors = []
for node in G.nodes():
    house = df[df['Character'] == node]['House_Allegiance'].iloc[0] if not df[df['Character'] == node].empty else 'Unknown'
    node_colors.append(DUNE_HOUSE_COLORS.get(house, '#CCCCCC'))

pos = nx.spring_layout(G, k=0.7, iterations=50, seed=42)

edge_x = []
edge_y = []
for source, target in G.edges():
    x0, y0 = pos[source]
    x1, y1 = pos[target]
    edge_x += [x0, x1, None]
    edge_y += [y0, y1, None]

edge_trace = go.Scatter(
    x=edge_x, y=edge_y,
    line=dict(width=1, color='#888'),
    hoverinfo='none',
    mode='lines'
)

node_x = []
node_y = []
hover_text = []
for node in G.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)
    info = df[df['Character'] == node].iloc[0] if not df[df['Character'] == node].empty else None
    hover = node
    if info is not None:
        hover += f"<br>House: {info['House_Allegiance'] or 'Unknown'}"
        hover += f"<br>Book: {info['Book'] or 'Unknown'}"
    hover_text.append(hover)

node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode='markers+text',
    hoverinfo='text',
    text=[node for node in G.nodes()],
    textposition="top center",
    marker=dict(
        showscale=False,
        color=node_colors,
        size=18,
        line_width=2,
        opacity=0.9
    ),
    hovertext=hover_text
)


fig_network = go.Figure(data=[edge_trace, node_trace],
            layout=go.Layout(
                title='Dune Character Relationship Network',
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                height=700
            )
        )
legend_traces = []
for house, color in DUNE_HOUSE_COLORS.items():
    legend_traces.append(
        go.Scatter(
            x=[None], y=[None], 
            mode='markers', 
            marker=dict(size=12, color=color),
            legendgroup=house,
            showlegend=True,
            name=house
        )
    )

fig_network.add_traces(legend_traces)
fig_network.update_layout(showlegend=True)

st.plotly_chart(fig_network, use_container_width=True)

