
import streamlit as st
import requests
import json
import os
import random
from datetime import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="MoodFlix OTT", layout="wide")

# --- 2. CUSTOM UI/CSS INJECTION ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom, #000000, #141414, #212121);
        color: white;
    }
    
    /* Ensuring all posters have the same height for a clean grid */
    [data-testid="stImage"] img {
        border-radius: 12px;
        transition: transform .3s ease;
        box-shadow: 0 4px 20px rgba(0,0,0,0.8);
        height: 400px;
        object-fit: cover;
    }
    
    [data-testid="stImage"] img:hover {
        transform: scale(1.05);
        border: 2px solid #E50914;
    }

    /* Sidebar Background */
    [data-testid="stSidebar"] {
        background-color: #0c0c0c;
        border-right: 1px solid #333;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONSTANTS ---
API_KEY = 'a49ff6bbc6fa0b98dc085b9ea7f04549'
BASE_URL = "https://api.themoviedb.org/3"
# The base URL for TMDB images - standardizing this is key
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500" 

# --- 4. DATA LOADING ---
def load_moods():
    try:
        with open('data/genres.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Missing data/genres.json file!")
        return {}

# --- 5. LOGIC FUNCTIONS ---
def get_movies_by_mood(genre_id):
    random_page = random.randint(1, 10)
    url = f"{BASE_URL}/discover/movie?api_key={API_KEY}&with_genres={genre_id}&sort_by=popularity.desc&page={random_page}"
    response = requests.get(url)
    return response.json().get('results', [])[:16]

def search_movies(query):
    url = f"{BASE_URL}/search/movie?api_key={API_KEY}&query={query}&language=en-US&page=1"
    response = requests.get(url)
    return response.json().get('results', [])[:16]

def save_to_history(action_type, detail):
    if not os.path.exists('result'):
        os.makedirs('result')
    with open('result/history.txt', 'a', encoding='utf-8') as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {action_type}: {detail}\n")

# --- 6. MAIN UI ---
def main():
    mood_map = load_moods()
    
    st.title("🎬 MoodFlix")
    
    # Sidebar
    st.sidebar.header("Search & Discovery")
    search_query = st.sidebar.text_input("Find a specific movie...")
    st.sidebar.divider()
    selected_mood = st.sidebar.selectbox("Feeling like...", list(mood_map.keys()))
    search_button = st.sidebar.button("Refresh Mood Picks")

    # Determine what to show
    if search_query:
        st.subheader(f"Results for: '{search_query}'")
        movies = search_movies(search_query)
    elif search_button or 'first_run' not in st.session_state:
        st.session_state['first_run'] = True
        st.subheader(f"Current Vibe: {selected_mood}")
        movies = get_movies_by_mood(mood_map[selected_mood])
    else:
        movies = []

    # --- DISPLAY GRID ---
    if movies:
        # We use a 4-column layout
        cols = st.columns(4)
        for i, movie in enumerate(movies):
            with cols[i % 4]:
                title = movie.get('title', 'Unknown Title')
                poster_path = movie.get('poster_path')
                rating = movie.get('vote_average', 0.0)
                
                # Check if the poster exists, otherwise use a placeholder
                if poster_path:
                    # Constructing the URL carefully
                    img_url = f"{IMAGE_BASE_URL}{poster_path}"
                else:
                    img_url = "https://via.placeholder.com/500x750?text=No+Poster+Available"
                
                # Display components
                st.image(img_url, use_column_width=True)
                st.write(f"**{title}**")
                st.caption(f"⭐ {rating}/10")
    elif search_query:
        st.warning("No movies found. Try a different title!")

if __name__ == "__main__":
    main()