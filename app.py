import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import uuid
import os
from dotenv import load_dotenv
load_dotenv()


# Load Spotify credentials from environment variables
def require_env(name):
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"Missing required environment variable: {name}")
    return value

SPOTIPY_CLIENT_ID = require_env("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = require_env("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = require_env("SPOTIPY_REDIRECT_URI")

SCOPE = "user-read-playback-state user-modify-playback-state user-read-currently-playing streaming"

st.title("🎶 SyncTune – Listen Together")

# Spotify Auth Setup
@st.cache_resource
def get_spotify_client():
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=SCOPE,
        show_dialog=True,
        open_browser=True
    ))

sp = get_spotify_client()

# Room Management
room_id = st.query_params.get("room")

def get_base_url():
    return os.getenv("BASE_URL", "http://localhost:8501")

if not room_id:
    if st.button("Create Room"):
        new_room_id = str(uuid.uuid4())
        st.query_params["room"] = new_room_id  # Set new room in query params
        room_link = f"{get_base_url()}/?room={new_room_id}"
        st.success(f"Room created! Share this link: {room_link}")
        st.stop()
else:
    st.success(f"Joined Room: {room_id}")

# Music Search and Playback
query = st.text_input("Search for a song:")
if query:
    results = sp.search(q=query, type="track", limit=5)
    for idx, item in enumerate(results['tracks']['items']):
        track_name = item['name']
        artists = ", ".join(artist['name'] for artist in item['artists'])
        track_uri = item['uri']
        st.write(f"{track_name} by {artists}")
        if st.button(f"Play: {track_name}", key=idx):
            sp.start_playback(uris=[track_uri])
            st.success("Playback started!")

# Playback Status
if st.button("Check Playback Status"):
    playback = sp.current_playback()
    if playback and playback.get('is_playing'):
        track = playback['item']
        st.write(f"Currently Playing: {track['name']} by {track['artists'][0]['name']}")
    else:
        st.write("No music is currently playing.")
