import spotipy
from spotipy.oauth2 import SpotifyOAuth

import configparser
import datetime
from dotenv import load_dotenv
import pathlib
import sys
import logging
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

""" Logging object to ouput to Airflow"""
logger = logging.getLogger("airflow.task")

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
    logger.warn(f"Error with file input. Error {e}")
    sys.exit(1)

date_dag_run = datetime.datetime.strptime(output_name, "%Y%m%d")

def main():

    start = time.perf_counter()

    sp = sp_connect()
    SP_CONNECT_TIME = time.perf_counter() - start
    print(f"sp_connect completed in: {SP_CONNECT_TIME:0.4f}s")

    start = time.perf_counter()
    logger.info("Extracting Playlist...")
    user_playlists = playlist_extraction(sp)
    E_PLAYLIST_TIME = time.perf_counter() - start
    print(f"playlists extraction completed in: {E_PLAYLIST_TIME:0.4f}s")

    start = time.perf_counter()
    logger.info("Transforming Playlist...")
    user_playlists_t = playlist_transformation(user_playlists)
    T_PLAYLIST_TIME = time.perf_counter() - start
    print(f"playlists transformation completed in: {T_PLAYLIST_TIME:0.4f}s")

    start = time.perf_counter()
    logger.info("Exporting Playlist...")
    load_to_csv(user_playlists_t, "playlist")
    L_PLAYLIST_TIME = time.perf_counter() - start
    print(f"playlists loading completed in: {L_PLAYLIST_TIME:0.4f}s")

    start = time.perf_counter()
    logger.info("Extracting Tracks...")
    user_tracks = tracks_extraction(sp, user_playlists)
    E_TRACK_TIME = time.perf_counter() - start
    print(f"track extraction completed in: {E_TRACK_TIME:0.4f}s")

    start = time.perf_counter() 
    logger.info("Transforming Tracks...")
    user_tracks_t = tracks_transformation(user_tracks)
    T_TRACK_TIME = time.perf_counter() - start
    print(f"track transformation completed in: {T_TRACK_TIME:0.4f}s")

    start = time.perf_counter()
    logger.info("Exporting Tracks...")
    load_to_csv(user_tracks_t, "tracks")
    L_TRACK_TIME = time.perf_counter() - start
    print(f"track loading completed in: {L_TRACK_TIME:0.4f}s")
    
""" Connect to Spotify API through Spotipy """
def sp_connect():
    try: 
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=SP_CLIENT_ID, client_secret=SP_SECRET, redirect_uri=SP_REDIRECT_URL))
        return sp
    except Exception as e:
        logger.warn(f"Unable to connect to API: {e}")
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
        start = time.perf_counter()
        print(f"{playlist_uri} started")
        user_tracks = pd.concat([user_tracks, retrive_playlist_tracks(sp, playlist_uri)], axis=0)
        print(f"{playlist_uri} total time: {time.perf_counter() - start:0.4f} seconds")
    
    return user_tracks

""" 
    Spotify API limits the response of tracks to 100
    so an offset is need to properly paginate through all
    playlists that a user has
"""
def retrive_playlist_tracks(sp, playlist_uri):

    start = time.perf_counter()

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
        print(f"-----Elapsed Time for {i}th: {time.perf_counter() - start:0.4f} seconds")
    
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