import streamlit as st
import pickle
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

@st.cache_resource
def load_data():
    movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    vectors = pickle.load(open('vectors.pkl', 'rb'))
    csv = pd.read_csv('TMDB_all_movies.csv')[['title', 'poster_path']].dropna()
    poster_map = dict(zip(csv['title'], csv['poster_path']))
    return movies, vectors, poster_map

movies, vectors, poster_map = load_data()

TMDB_BASE = "https://image.tmdb.org/t/p/w300"

def recommend(movie):
    matches = movies[movies['title'].str.lower() == movie.strip().lower()]
    if matches.empty:
        return None, f"Movie '{movie}' not found in the dataset."
    idx = matches.index[0]
    scores = cosine_similarity(vectors[idx], vectors).flatten()
    top_indices = scores.argsort()[::-1][1:6]
    results = []
    for i in top_indices:
        title = movies.iloc[i]['title']
        poster = poster_map.get(title)
        poster_url = TMDB_BASE + poster if poster else None
        results.append((title, poster_url))
    return results, None

st.markdown("""
<style>
  /* Deep cinematic gradient background */
  [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0d0d1a 0%, #1a0a2e 40%, #0a1628 100%);
    min-height: 100vh;
  }
  [data-testid="stHeader"] {
    background: transparent !important;
  }

  /* Styled input box */
  input[type="text"] {
    background-color: #1e1e3a !important;
    color: #e0e0ff !important;
    border: 1px solid #6c63ff !important;
    border-radius: 10px !important;
  }

  /* Recommend button */
  div.stButton > button {
    background: linear-gradient(90deg, #6c63ff, #a855f7);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.5rem 2rem;
    font-size: 16px;
    font-weight: 600;
    transition: opacity 0.2s;
  }
  div.stButton > button:hover {
    opacity: 0.85;
  }

  /* Result text */
  .stWrite, p, label {
    color: #d0d0ff !important;
  }

  /* Divider */
  hr { border-color: #6c63ff44; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='font-size:60px;color:#e8e0ff;'>Movie Recommender System</h1>", unsafe_allow_html=True)
st.markdown(
    "<link href='https://fonts.googleapis.com/css2?family=Playfair+Display:ital@1&display=swap' rel='stylesheet'>"
    "<p style='font-size:32px;color:#a78bfa;font-family:Playfair Display,serif;font-style:italic;'>"
    "What's the mood today?</p>",
    unsafe_allow_html=True
)

movie_name = st.text_input('Enter a movie name:')

if st.button('Recommend'):
    if not movie_name.strip():
        st.warning("Please enter a movie name.")
    else:
        results, error = recommend(movie_name)
        if error:
            st.error(error)
        else:
            st.subheader("Movies you might like:")
            cols = st.columns(5)
            for col, (title, poster_url) in zip(cols, results):
                with col:
                    if poster_url:
                        st.image(poster_url, use_container_width=True)
                    else:
                        st.markdown("🎬")
                    st.caption(title)

st.markdown("---")
st.markdown("Made by **AryanMandlik**")
