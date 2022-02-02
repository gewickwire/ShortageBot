import json
import os
import re

from urllib.parse import urlparse, parse_qs
from pathlib import Path
from config import config
from . import ShortageDB

import logging

import requests
from bs4 import BeautifulSoup

ashp_base_detail_url = 'https://www.ashp.org/drug-shortages/current-shortages/drug-shortage-detail.aspx?id='


class ASHPitem:
    #an item in the ASHP drug list
    def __init__(self,
                 name: str,
                 ashp_id: int = None,
                 detailurl: str = None,
                 ):
        self.drugname = name
        self.ashp_id = ashp_id or int(parse_qs(urlparse(detailurl).query).get('id')[0])
    
    @property
    def detailurl(self):
        #get detail url
        return ashp_base_detail_url + str(self.ashp_id)

class ChangeTrk:
    def __init__(self):
        global local_list
        local_list = self._getlocallist(self)
        global live_list
        live_list = self._getlivelist(self)
        global local_ids
        local_ids = self._getlocalids()
        global online_ids
        online_ids = self._getonlineids()
        global new_shortages
        self.new_shortages = self.findnewshorts()
        global resolved_shortages
        self.resolved_shortages = self.findoldshorts()
        global save
        save = []
        global remove
        remove = []
        
        if self.resolved_shortages:
            self.remove_resolved()
        if self.new_shortages:
            self.add_new()
        
        self._update_db()

    def _getlocallist(self, local_list):
        db_path = config["DB_FILE"]
        database = ShortageDB.read(self, db_path)
        local_list = []
        local_item = []
        for item in database:
            local_item = {"ashp_id": item["ashp_id"], "drugname": item["drugname"], "detailurl": item["detailurl"]}
            local_list.append(local_item)
        return local_list

    def _getlivelist(self, live_list):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s : %(levelname)s : %(message)s')

        logging.info('Checking current online ASHP shortage list for updates...')
        online_list_url = 'https://www.ashp.org/drug-shortages/current-shortages/drug-shortages-list?page=CurrentShortages'
        online_shortage_list = requests.get(online_list_url)

        if online_shortage_list.status_code != 200:
            logging.error('Cannot reach ASHP website!')
            exit()
        
        live_list = []
        active_shortage = []
        soup = BeautifulSoup(online_shortage_list.content, 'html.parser')
        for link in soup.find(id='1_dsGridView').find_all('a'):
            idregex = re.search("id=\d+", str(link))
            idnumber = re.search("\d+", idregex.group())
            active_shortage = {"ashp_id": int(idnumber.group()), "drugname": link.get_text(), "detailurl": link.get('href')}
            live_list.append(active_shortage)
        return live_list

    def _getonlineids(self):
        online_ids = []
        for i in range(len(live_list)):
            item = live_list[i]
            liveid = item["ashp_id"]
            online_ids.append(liveid)
        return online_ids
        
    def _getlocalids(self):
        local_ids = []
        for i in range(len(local_list)):
            item = local_list[i]
            localid = item["ashp_id"]
            local_ids.append(localid)
        return local_ids
        
    def findnewshorts(self):    
        global new_shortages
        new_shortages = []
        for i in range(len(live_list)):
            item = live_list[i]
            tempid = item["ashp_id"]
            if tempid not in local_ids:
                new_shortages.append(item)
        return new_shortages
        
    def findoldshorts(self):    
        global resolved_shortages
        resolved_shortages = []
        for i in range(len(local_list)):
            item = local_list[i]
            tempid = item["ashp_id"]
            if tempid not in online_ids:
                resolved_shortages.append(tempid)
        return resolved_shortages

    def remove_resolved(self):
        global remove
        remove = []
        db_path = config["DB_FILE"]
        database = ShortageDB.read(self, db_path)
        for i in range(len(database)):
            item = database[i]
            tempid = item["ashp_id"]
            for j in range(len(resolved_shortages)):
                if tempid in resolved_shortages:
                    remove.append(tempid)
                    database.pop(j)
                else:
                    save.append(item)

    def add_new(self):
        for i in range(len(new_shortages)):
            item = new_shortages[i]
            save.append(item)

    def _update_db(self):
        #first add all old ones not yet resolved back, then save it all again.
        db_path = config["DB_FILE"]
        database = ShortageDB.read(self, db_path)
        for i in range(len(database)):
            item = database[i]
            save.append(item)
        ShortageDB.store(self, db_path, save)