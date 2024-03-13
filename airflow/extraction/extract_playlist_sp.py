import spotipy
from spotipy.oauth2 import SpotifyOAuth

import configparser
import datetime
from dotenv import load_dotenv
import pathlib
import sys
import time

import pandas as pd
import numpy as np
import math

from playlist import Playlist

"""
    TODO: Basic Transformations of the dataframes
    TODO: Set up Airflow DAG and unblock command line arguments
"""

""" Load enviorment variables and set scope for Spotipy authorization flow"""
load_dotenv()
scope = "playlist-read-private"

""" Read Config File """
parser = configparser.ConfigParser()
script_path = pathlib.Path(__file__).parent.resolve()
config_file = "config.conf"
parser.read(f"{script_path}/{config_file}")

""" Set Variables from Config """
SP_SECRET = parser.get("spotipy_config", "client_secret")
SP_CLIENT_ID = parser.get("spotipy_config", "client_id")

""" 
    Use command line argument as output file
    name and also store as column value
"""
# try:
#     output_name = sys.argv[1]
# except Exception as e:
#     print(f"Error with file input. Error {e}")
#     sys.exit(1)
# date_dag_run = datetime.datetime.strptime(output_name, "%Y%m%d")

def main():
    sp = sp_connect()
    user_playlists = extract_user_playlists(sp)
    load_to_csv(user_playlists, "playlist")
    user_tracks = extract_playlist_tracks(sp, user_playlists)
    load_to_csv(user_tracks, "tracks")
    
""" Connect to Spotify API through Spotipy """
def sp_connect():
    try: 
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
        return sp
    except Exception as e:
        print(f"Unable to connect to API: {e}")
        sys.exit(1)


""" API Extraction """
""" 
    Spotify API limits the response of playlists to 50
    so an offset is need to properly paginate through all
    playlists that a user has
"""
def extract_user_playlists(sp):
    offset = 0
    playlists = sp.current_user_playlists(offset = offset)
    total_items = playlists['total']
    user_playlists = list()

    for i in range(math.ceil(total_items / 50)):
        for playlist in playlists['items']:
            user_playlists.append(playlist)
        offset += 50
        playlists = sp.current_user_playlists(offset = offset)
    
    return pd.DataFrame(user_playlists)

""" Retreiving every track from each playlist using URI """
def extract_playlist_tracks(sp, user_playlists):
    user_tracks = pd.DataFrame()
    for playlist_uri in user_playlists['uri']:
        user_tracks = pd.concat([user_tracks, get_tracks_from_playlist(sp, playlist_uri)], axis=0)
    
    return user_tracks

""" 
    Spotify API limits the response of tracks to 100
    so an offset is need to properly paginate through all
    playlists that a user has
"""
def get_tracks_from_playlist(sp, playlist_uri):

    offset = 0
    playlist_tracks = sp.playlist_tracks(playlist_uri, offset = offset)
    total_items = playlist_tracks['total']
    tracks = list()

    for i in range(math.ceil(total_items / 50)):
        for track in playlist_tracks['items']:
            tracks.append(track)
        offset += 50
        playlist_tracks = sp.playlist_tracks(playlist_uri, offset = offset)
    
    return pd.DataFrame(tracks)


""" CSV Formatting"""
def load_to_csv(df, type):
    df.to_csv(f"{script_path}/tmp/{type}.csv", index=False)



if __name__ == "__main__":
    main()