import os

import spotipy
from spotipy.oauth2 import SpotifyOAuth

os.environ['SPOTIPY_CLIENT_ID'] = "***"
os.environ['SPOTIPY_CLIENT_SECRET'] = "***"
os.environ['SPOTIPY_REDIRECT_URI'] = 'http://localhost:8080/callback'

scope = 'user-read-currently-playing user-read-playback-state user-modify-playback-state'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))


def next_track():
    sp.next_track('0d86ccc3eab458e328456e3bd4898100f5187798')


def prev_track():
    sp.previous_track('0d86ccc3eab458e328456e3bd4898100f5187798')


def pause_play(state):
    if not state:
        sp.start_playback('0d86ccc3eab458e328456e3bd4898100f5187798')
        return "play"

    elif state:
        sp.pause_playback('0d86ccc3eab458e328456e3bd4898100f5187798')
        return "pause"


def seekToPosition(pos):
    sp.seek_track(int(pos), '0d86ccc3eab458e328456e3bd4898100f5187798')


def getSongInfo():
    results = sp.current_user_playing_track()
    if results == None:
        sp.start_playback('0d86ccc3eab458e328456e3bd4898100f5187798')
        sp.pause_playback('0d86ccc3eab458e328456e3bd4898100f5187798')
        results = sp.current_user_playing_track()

    artistName = []
    if len(results['item']['artists']) == 0:
        artistName.append(results['item']['artists'][0]['name'])
    else:
        for x in results['item']['artists']:
            artistName.append(x['name'])
            artistName.append(", ")

        artistName = artistName[:-1]

    actual = results['progress_ms']
    duration = results['item']['duration_ms']

    songTitle = results['item']['name']
    isPlaying = results["is_playing"]
    url = results['item']['album']['images'][1]['url']

    return artistName, songTitle, isPlaying, url, actual, duration
