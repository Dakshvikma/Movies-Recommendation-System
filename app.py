

import pickle
import streamlit as st
import requests
import pandas as pd

def fetch_poster(movie_title):
    """Fetch movie poster from OMDb API"""
    
    movie_title = movie_title.replace(" ", "+")
    url = f"http://www.omdbapi.com/?apikey=de9f57db&t={movie_title}"

    try:
        data = requests.get(url, timeout=10)
        data.raise_for_status()
        data = data.json()

        poster = data.get("Poster")

        if poster and poster != "N/A":
            return poster

    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching poster: {e}")

    return "https://placehold.co/500x750/333/FFFFFF?text=No+Poster"


def recommend(movie):
    """Recommends 5 similar movies based on the selected movie."""
    try:
        index = movies[movies['title'] == movie].index[0]
    except IndexError:
        st.error("Movie not found in the dataset. Please select another one.")
        return [], [], [], []
        
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    
    recommended_movie_names = []
    recommended_movie_posters = []
    recommended_movie_years = []
    recommended_movie_ratings = []

    for i in distances[1:6]:
        movie_title = movies.iloc[i[0]].title
    
        recommended_movie_posters.append(fetch_poster(movie_title))
        recommended_movie_names.append(movie_title)
        recommended_movie_years.append(movies.iloc[i[0]].year)
        recommended_movie_ratings.append(movies.iloc[i[0]].vote_average)

    return recommended_movie_names, recommended_movie_posters, recommended_movie_years, recommended_movie_ratings


st.set_page_config(layout="wide")
st.header('Movie Recommender System Using Machine Learning')

# Load the data files
try:
    movies_dict = pickle.load(open('artifacts/movie_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('artifacts/similarity.pkl', 'rb'))
except FileNotFoundError:
    st.error("Model files not found. Please run the data processing notebook first.")
    st.stop()


movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

if st.button('Show Recommendation'):
    with st.spinner('Finding recommendations...'):
        recommended_movie_names, recommended_movie_posters, recommended_movie_years, recommended_movie_ratings = recommend(selected_movie)
    
    if recommended_movie_names:
        cols = st.columns(5)
        for i, col in enumerate(cols):
            with col:
                st.text(recommended_movie_names[i])
                st.image(recommended_movie_posters[i])
                # Ensure year is an integer before displaying
                year = recommended_movie_years[i]
                if pd.notna(year):
                    st.caption(f"Year: {int(year)}")
                else:
                    st.caption("Year: N/A")
                
                rating = recommended_movie_ratings[i]
                st.caption(f"Rating: {rating:.1f} ⭐")
