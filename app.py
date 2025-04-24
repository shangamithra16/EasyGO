import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

# Streamlit secrets (credentials)
CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
REDIRECT_URI = st.secrets["REDIRECT_URI"]

# Initialize Spotipy client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope="user-library-read user-read-playback-state user-modify-playback-state",
                                              open_browser=True))


# Initialize Streamlit session state if not already initialized
if 'room_id' not in st.session_state:
    st.session_state['room_id'] = None
if 'track_uri' not in st.session_state:
    st.session_state['track_uri'] = None
if 'playback_status' not in st.session_state:
    st.session_state['playback_status'] = 'paused'

# Function to create or join a room
def create_or_join_room():
    room_id = st.text_input("Enter a Room ID (or create a new one):")
    if room_id:
        st.session_state['room_id'] = room_id
        st.write(f"Room {room_id} selected.")
        return True
    return False

# Function to search for music
def search_music(query):
    query = st.text_input("Search for music:")

    if query:
        with st.spinner("Searching..."):
            track_names, track_uris = search_music(query)
            ...

    results = sp.search(q=query, type="track", limit=5)
    
    if not results['tracks']['items']:
        st.write("No tracks found for your query. Please try a different search.")
        return [], []
    
    tracks = results['tracks']['items']
    track_names = [track['name'] for track in tracks]
    track_uris = [track['uri'] for track in tracks]
    
    return track_names, track_uris

# Function to start playback
def start_playback():
    if st.session_state['track_uri']:
        sp.start_playback(uris=[st.session_state['track_uri']])

# Function to pause playback
def pause_playback():
    sp.pause_playback()

# Streamlit interface
st.title("Music Sync App")
query = st.text_input("Search for music:")

# Room Management (Create or Join Room)
if create_or_join_room():
    st.session_state['track_uri'] = None  # Reset previous track URI
    
    # Music Search
    
    if query:
        track_names, track_uris = search_music(query)
        if track_names:
            st.write("Select a track:")
            selected_track = st.selectbox("Choose a song:", track_names)
            if selected_track:
                track_index = track_names.index(selected_track)
                st.session_state['track_uri'] = track_uris[track_index]
                st.write(f"Selected Track: {selected_track}")

                # Control buttons to synchronize playback
                play_button = st.button("Play")
                pause_button = st.button("Pause")

                if play_button:
                    start_playback()
                    st.session_state['playback_status'] = 'playing'

                if pause_button:
                    pause_playback()
                    st.session_state['playback_status'] = 'paused'

# Display playback status
st.write(f"Playback Status: {st.session_state['playback_status']}")

