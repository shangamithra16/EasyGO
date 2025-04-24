import streamlit as st
import asyncio
import aiohttp
import uuid

# Spotify credentials from Streamlit secrets
CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
REDIRECT_URI = st.secrets["REDIRECT_URI"]

# Define Spotify OAuth and headers
BASE_URL = "https://api.spotify.com/v1"
headers = {
    "Authorization": f"Bearer {st.secrets['SPOTIFY_ACCESS_TOKEN']}"
}

# Spotify API Request Function (Async)
async def fetch_spotify_data(url, params=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                st.error(f"Error fetching data: {response.status}")
                return None

# Playback control functions (as in your original code)
def start_playback(track_uri):
    # Start playback with the selected track URI
    sp.start_playback(uris=[track_uri])

def pause_playback():
    sp.pause_playback()

# Streamlit UI Setup
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

    # Language categories (as before)
    language_to_category_id = {
        "Tamil": "0JQ5DAqbMKFEC4WFtoNRpw",
        "Hindi (Bollywood)": "0JQ5DAqbMKFEC4WFtoNRpw",
        "Telugu": "0JQ5DAqbMKFAXlCG6QvYQ4",
        "Punjabi": "0JQ5DAqbMKFCfObibaOZbv",
        "English": "0JQ5DAqbMKFDXXwE9BDJAr"
    }

    st.subheader("🎵 Choose Music Language")
    selected_language = st.selectbox("Pick a language:", list(language_to_category_id.keys()))
    category_id = language_to_category_id[selected_language]

    # Fetch trending playlists asynchronously
    async def fetch_playlists():
        playlists_url = f"{BASE_URL}/browse/categories/{category_id}/playlists"
        playlists_data = await fetch_spotify_data(playlists_url, {"country": "IN", "limit": 5})
        if playlists_data:
            return playlists_data['playlists']['items']
        return []

    playlists = asyncio.run(fetch_playlists())

    if playlists:
        playlist_names = [pl['name'] for pl in playlists]
        selected_playlist_name = st.selectbox("Choose a playlist:", playlist_names)

        if selected_playlist_name:
            selected_playlist = next(pl for pl in playlists if pl['name'] == selected_playlist_name)
            playlist_id = selected_playlist['id']

            # Fetch songs from the selected playlist asynchronously
            async def fetch_tracks():
                tracks_url = f"{BASE_URL}/playlists/{playlist_id}/tracks"
                tracks_data = await fetch_spotify_data(tracks_url, {"limit": 20})
                if tracks_data:
                    return tracks_data['items']
                return []

            tracks = asyncio.run(fetch_tracks())
            if tracks:
                track_names = [item['track']['name'] + " - " + item['track']['artists'][0]['name'] for item in tracks]
                track_uris = [item['track']['uri'] for item in tracks]

                selected_track = st.selectbox("🎧 Choose a song:", track_names)
                if selected_track:
                    index = track_names.index(selected_track)
                    st.session_state['track_uri'] = track_uris[index]
                    st.write(f"🎶 Selected Track: {selected_track}")

                    if st.button("▶️ Play"):
                        start_playback(st.session_state['track_uri'])
                    if st.button("⏸️ Pause"):
                        pause_playback()
    else:
        st.write("No playlists found for the selected language.")

    # Optional: manual search fallback
    st.markdown("---")
    st.subheader("🔍 Or search manually")
    query = st.text_input("Search for music:")
    if query:
        async def search_music():
            search_url = f"{BASE_URL}/search"
            search_results = await fetch_spotify_data(search_url, {"q": query, "type": "track", "limit": 5})
            if search_results:
                return search_results['tracks']['items']
            return []

        search_results = asyncio.run(search_music())
        if search_results:
            names = [t['name'] + " - " + t['artists'][0]['name'] for t in search_results]
            uris = [t['uri'] for t in search_results]

            selected_manual = st.selectbox("Choose from search:", names, key="manual")
            if selected_manual:
                idx = names.index(selected_manual)
                st.session_state['track_uri'] = uris[idx]
                st.write(f"🎶 Selected Track: {selected_manual}")

# Show playback status
st.write(f"📡 Playback Status: {st.session_state['playback_status']}")
