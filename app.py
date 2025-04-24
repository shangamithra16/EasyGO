import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import threading
import time
import uuid

# Access the Spotify credentials from Streamlit secrets
CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
REDIRECT_URI = st.secrets["REDIRECT_URI"]

# Initialize Spotipy client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope="user-library-read user-read-playback-state user-modify-playback-state"))

# Streamlit session state to track room and playback status
if 'room_id' not in st.session_state:
    st.session_state['room_id'] = None
if 'track_uri' not in st.session_state:
    st.session_state['track_uri'] = None
if 'playback_status' not in st.session_state:
    st.session_state['playback_status'] = 'paused'

# Function to start playback
def start_playback():
    if st.session_state['track_uri']:
        sp.start_playback(uris=[st.session_state['track_uri']])

# Function to pause playback
def pause_playback():
    sp.pause_playback()

# Function to search for music
def search_music(query):
    results = sp.search(q=query, type="track", limit=5)
    tracks = results['tracks']['items']
    track_names = [track['name'] for track in tracks]
    track_uris = [track['uri'] for track in tracks]
    return track_names, track_uris

# Streamlit interface
st.title("🎵 Music Sync App")

# Room selection
st.subheader("Room Setup")
room_action = st.radio("Do you want to create a new room or join an existing one?", ["Create Room", "Join Room"])

if room_action == "Create Room":
    if st.button("Generate Room"):
        new_room_id = str(uuid.uuid4())[:8]
        st.session_state['room_id'] = new_room_id
        st.success(f"Room Created! Your Room ID is: {new_room_id}")
        st.markdown(f"🔗 Shareable link: `{st.request.url}?room_id={new_room_id}`")
elif room_action == "Join Room":
    room_id_input = st.text_input("Enter Room ID to join:")
    if room_id_input:
        st.session_state['room_id'] = room_id_input
        st.success(f"Joined Room: {room_id_input}")

# Proceed if room is active
if st.session_state['room_id']:
    st.write(f"🛋️ Active Room ID: `{st.session_state['room_id']}`")

    # Language selection
    st.subheader("Select Language for Music Search")
    languages = ["Tamil", "Hindi", "Telugu", "Malayalam", "Kannada", "Punjabi", "Bengali", "Gujarati", "Marathi", "English"]
    selected_language = st.radio("Choose a language:", languages)

    # Music search
    query = st.text_input("Search for music:")
    if query:
        full_query = f"{query} {selected_language} song"
        track_names, track_uris = search_music(full_query)
        if track_names:
            st.write("Select a track:")
            selected_track = st.selectbox("Choose a song:", track_names)
            if selected_track:
                track_index = track_names.index(selected_track)
                st.session_state['track_uri'] = track_uris[track_index]

                st.write(f"🎶 Selected Track: {selected_track}")
                
                # Playback controls
                play_button = st.button("▶️ Play")
                pause_button = st.button("⏸️ Pause")

                if play_button:
                    start_playback()
                    st.session_state['playback_status'] = 'playing'

                if pause_button:
                    pause_playback()
                    st.session_state['playback_status'] = 'paused'
        else:
            st.warning("No tracks found. Try a different query or language.")

    # Show playback status
    st.write(f"Playback Status: {st.session_state['playback_status']}")
