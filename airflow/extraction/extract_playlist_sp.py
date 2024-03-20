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
    TODO: Set up Airflow DAG and unblock command line arguments
    TODO: Implement audio feature extractions
    TODO: Write playlist and tracks classes
"""

""" Load Spotipy credentials and set scope for Spotipy authorization flow"""
scope = "playlist-read-private"

""" Read Config File """
parser = configparser.ConfigParser()
script_path = pathlib.Path(__file__).parent.resolve()
config_file = "config.conf"
parser.read(f"{script_path}/{config_file}")

""" Set Variables from Config """
SP_SECRET = parser.get("spotipy_config", "client_secret")
SP_CLIENT_ID = parser.get("spotipy_config", "client_id")
SP_REDIRECT_URL = parser.get("spotipy_config", "redirect_uri")

""" 
    Use command line argument as output file
    name and also store as column value
"""
try:
    output_name = sys.argv[1]
except Exception as e:
    print(f"Error with file input. Error {e}")
    sys.exit(1)
date_dag_run = datetime.datetime.strptime(output_name, "%Y%m%d")

def main():
    sp = sp_connect()
    print("Extracting Playlist...")
    user_playlists = playlist_extraction(sp)
    print("Transforming Playlist...")
    user_playlists_t = playlist_transformation(user_playlists)
    print("Exporting Playlist...")
    load_to_csv(user_playlists_t, "playlist")

    print("Extracting Tracks...")
    user_tracks = tracks_extraction(sp, user_playlists)
    print("Transforming Tracks...")
    user_tracks_t = tracks_transformation(user_tracks)
    print("Exporting Tracks...")
    load_to_csv(user_tracks_t, "tracks")
    
""" Connect to Spotify API through Spotipy """
def sp_connect():
    try: 
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=SP_CLIENT_ID, client_secret=SP_SECRET, redirect_uri=SP_REDIRECT_URL))
        return sp
    except Exception as e:
        print(f"Unable to connect to API: {e}")
        sys.exit(1)


""" API Extraction """ #########
""" 
    Spotify API limits the response of playlists to 50
    so an offset is need to properly paginate through all
    playlists that a user has
"""
def playlist_extraction(sp):
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
def tracks_extraction(sp, user_playlists):
    user_tracks = pd.DataFrame()
    for playlist_uri in user_playlists['uri']:
        user_tracks = pd.concat([user_tracks, retrive_playlist_tracks(sp, playlist_uri)], axis=0)
    
    return user_tracks

""" 
    Spotify API limits the response of tracks to 100
    so an offset is need to properly paginate through all
    playlists that a user has
"""
def retrive_playlist_tracks(sp, playlist_uri):

    offset = 0
    playlist_tracks = sp.playlist_tracks(playlist_uri, offset = offset)
    total_items = playlist_tracks['total']
    tracks = list()

    for i in range(math.ceil(total_items / 50)):
        for track in playlist_tracks['items']:
            if track['track'] != None:
                tracks.append(track['track'])
        offset += 50
        playlist_tracks = sp.playlist_tracks(playlist_uri, offset = offset)
    
    return pd.DataFrame(tracks)

""" Transformations of dataframes """ ########

def playlist_transformation(playlist_df):
    playlist_df.dropna()
    playlist_df = playlist_df.drop(['collaborative', 'description','external_urls', 'href', 'public', 'primary_color', 'images', 'snapshot_id', 'type'], axis=1)

    playlist_df['owner'] = playlist_df['owner'].apply(lambda x : x.get('display_name'))
    playlist_df['total'] = playlist_df['tracks'].apply(lambda x : x.get('total'))
    playlist_df = playlist_df.drop(['tracks'], axis=1)

    playlist_df.set_index('uri', inplace=True)

    return playlist_df
    

def tracks_transformation(track_df):
    track_df.dropna()
    track_df = track_df.drop(['preview_url' ,'available_markets', 'explicit', 'type', 'episode', 'track', 'album', 'artists', 
                              'disc_number', 'track_number' , 'duration_ms' , 'external_ids','external_urls','href', 'is_local'], axis = 1)
    
    track_df.set_index('uri', inplace=True)
    
    return track_df


""" CSV Formatting""" ########
def load_to_csv(df, type):
    df.to_csv(f"{script_path}/tmp/{type}_{output_name}.csv", mode='w')



if __name__ == "__main__":
    main()