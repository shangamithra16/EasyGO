import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Spotify credentials
CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")

# App setup
st.title("🎵 Simple Music Player")
st.write("Search and play your favorite songs!")

# Authentication function
def authenticate_spotify():
    auth_manager = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope="user-library-read user-modify-playback-state streaming",
        cache_path=".cache"
    )
    return spotipy.Spotify(auth_manager=auth_manager)

# Initialize Spotify client
if 'sp' not in st.session_state:
    try:
        st.session_state.sp = authenticate_spotify()
        st.success("Connected to Spotify!")
    except Exception as e:
        st.error(f"Authentication failed: {str(e)}")
        st.stop()

# Search and play functionality
search_query = st.text_input("Search for songs, artists, or albums:")
if search_query:
    results = st.session_state.sp.search(q=search_query, type="track", limit=10)
    
    st.subheader("Search Results")
    for idx, track in enumerate(results['tracks']['items']):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"**{track['name']}** by {', '.join(artist['name'] for artist in track['artists'])}")
        with col2:
            if st.button("▶️ Play", key=f"play_{idx}"):
                try:
                    st.session_state.sp.start_playback(uris=[track['uri']])
                    st.success(f"Now playing: {track['name']}")
                except Exception as e:
                    st.error(f"Couldn't play track: {str(e)}")

# Player controls
st.subheader("Player Controls")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("⏸️ Pause"):
        st.session_state.sp.pause_playback()
with col2:
    if st.button("▶️ Resume"):
        st.session_state.sp.start_playback()
with col3:
    if st.button("⏭️ Next Track"):
        st.session_state.sp.next_track()

# Current playback info
if st.button("ℹ️ Show Current Track"):
    try:
        current = st.session_state.sp.current_playback()
        if current and current['is_playing']:
            track = current['item']
            st.write(f"**Now Playing:** {track['name']} by {', '.join(artist['name'] for artist in track['artists'])}")
        else:
            st.write("No track currently playing")
    except:
        st.warning("Couldn't fetch playback info")
