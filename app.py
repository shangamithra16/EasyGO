import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import uuid

# Spotify credentials from Streamlit secrets
CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
REDIRECT_URI = st.secrets["REDIRECT_URI"]

# Spotify client setup
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope="user-library-read user-read-playback-state user-modify-playback-state"))

# Session state
if 'room_id' not in st.session_state:
    st.session_state['room_id'] = None
if 'track_uri' not in st.session_state:
    st.session_state['track_uri'] = None
if 'playback_status' not in st.session_state:
    st.session_state['playback_status'] = 'paused'

# Playback control
def start_playback():
    if st.session_state['track_uri']:
        sp.start_playback(uris=[st.session_state['track_uri']])

def pause_playback():
    sp.pause_playback()

# UI setup
st.title("🎶 Music Sync App with Live Spotify Data")

# Room management
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

if st.session_state['room_id']:
    st.write(f"🛋️ Active Room ID: `{st.session_state['room_id']}`")

    # Step 1: Language categories (manually mapped to Spotify category IDs)
    language_to_category_id = {
        "Tamil": "0JQ5DAqbMKFEC4WFtoNRpw",   # ID may vary
        "Hindi (Bollywood)": "0JQ5DAqbMKFEC4WFtoNRpw",
        "Telugu": "0JQ5DAqbMKFAXlCG6QvYQ4",
        "Punjabi": "0JQ5DAqbMKFCfObibaOZbv",
        "English": "0JQ5DAqbMKFDXXwE9BDJAr"
    }

    st.subheader("🎵 Choose Music Language")
    selected_language = st.selectbox("Pick a language:", list(language_to_category_id.keys()))
    category_id = language_to_category_id[selected_language]

    # Step 2: Fetch playlists for that category
    st.subheader(f"🎼 Trending Playlists in {selected_language}")
    playlists = sp.category_playlists(category_id=category_id, country="IN", limit=5)['playlists']['items']
    playlist_names = [pl['name'] for pl in playlists]
    selected_playlist_name = st.selectbox("Choose a playlist:", playlist_names)

    if selected_playlist_name:
        selected_playlist = next(pl for pl in playlists if pl['name'] == selected_playlist_name)
        playlist_id = selected_playlist['id']

        # Step 3: Get songs from playlist
        tracks = sp.playlist_items(playlist_id, limit=20)['items']
        track_names = [item['track']['name'] + " - " + item['track']['artists'][0]['name'] for item in tracks]
        track_uris = [item['track']['uri'] for item in tracks]

        selected_track = st.selectbox("🎧 Choose a song:", track_names)
        if selected_track:
            index = track_names.index(selected_track)
            st.session_state['track_uri'] = track_uris[index]
            st.write(f"🎶 Selected Track: {selected_track}")

            if st.button("▶️ Play"):
                start_playback()
                st.session_state['playback_status'] = 'playing'
            if st.button("⏸️ Pause"):
                pause_playback()
                st.session_state['playback_status'] = 'paused'

    # Optional: manual search fallback
    st.markdown("---")
    st.subheader("🔍 Or search manually")
    query = st.text_input("Search for music:")
    if query:
        search_results = sp.search(q=query, type="track", limit=5)
        results = search_results['tracks']['items']
        names = [t['name'] + " - " + t['artists'][0]['name'] for t in results]
        uris = [t['uri'] for t in results]

        selected_manual = st.selectbox("Choose from search:", names, key="manual")
        if selected_manual:
            idx = names.index(selected_manual)
            st.session_state['track_uri'] = uris[idx]
            st.write(f"🎶 Selected Track: {selected_manual}")

# Show playback status
st.write(f"📡 Playback Status: {st.session_state['playback_status']}")
