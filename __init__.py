import json
import os

from config import config

class ShortageDB:
    def __init__(self,db_path):
        with open(db_path) as f:
        DB = json.load(f)
    
    def store(self, store):
        with open(db_path, 'w') as fp:
            json.dump(store, fp)