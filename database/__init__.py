import json
import os

from config import config

class ShortageDB:
    
    def read(self,db_path):
        with open(db_path) as f:
            DB = json.load(f)
        return DB
    
    def store(self, db_path, data):
        with open(db_path, 'w') as fp:
            json.dumps(data, indent=4)