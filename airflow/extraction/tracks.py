from datetime import datetime
from pathlib import Path  
import pandas as pd

class Track():

    def __init__(self, sp, uri, parent_uri) -> None:
        self.uri = uri
        self.id = self.get_id()
        self.name= self.get_name()
        self.popularity = self.get_popularity()
        self.features = self.get_features()
        self.parent_uri = parent_uri

    def get_id():
        pass

    def get_name():
        pass

    def get_features():
        pass

    def get_popularity():
        pass
