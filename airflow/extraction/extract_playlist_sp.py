import spotipy
from spotipy.oauth2 import SpotifyOAuth

import configparser
import datetime
from dotenv import load_dotenv
import pathlib
import sys

import pandas as pd
import numpy as np
import math

from playlist import Playlist

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
    print(user_playlists)


def sp_connect():
    """ Connect to Spotify API through Spotipy """
    try: 
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
        return sp
    except Exception as e:
        print(f"Unable to connect to API: {e}")
        sys.exit(1)

def extract_user_playlists(sp):
    """ 
        Spotify API limits the response of playlists to 50
        so and offset is need to properly paginate through all
        playlists that a user has
    """
    offset = 0
    playlists = sp.current_user_playlists(offset = offset)
    total_items = playlists['total']
    user_playlists = []

    for i in range(math.ceil(total_items / 50)):
        for playlist in playlists['items']:
            user_playlists.append(playlist)
        offset += 50
        playlists = sp.current_user_playlists(offset = offset)
    
    return pd.DataFrame(user_playlists)
    


if __name__ == "__main__":
    main()