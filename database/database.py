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
        self._getlocallist(self)
        self._getlivelist(self)
        self.local_list = []
        self.live_list = []
        self.new_shortages = None
        self.resolved_shortages = None
        self._compare_previous()

    def _getlocallist(self, local_list):
        db_path = config["DB_FILE"]
        database = ShortageDB.read(self, db_path)
        local_list = []
        for item in database:
            local_list.append(ASHPitem(
                name = item["drugname"],
                ashp_id = item["ashp_id"]
            ))

    def _getlivelist(self, live_list):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s : %(levelname)s : %(message)s')

        logging.info('Checking current online ASHP shortage list for updates...')
        online_list_url = 'https://www.ashp.org/drug-shortages/current-shortages/drug-shortages-list?page=CurrentShortages'
        online_shortage_list = requests.get(online_list_url)

        if online_shortage_list.status_code != 200:
            logging.error('Cannot reach ASHP website!')
            exit()
        
        live_list = []
        soup = BeautifulSoup(online_shortage_list.content, 'html.parser')
        for link in soup.find(id='1_dsGridView').find_all('a'):
            idregex = re.search("id=[0-9][0-9]?[0-9]?[0-9]?", str(link))
            idnumber = re.sub("id=", "", idregex.string)
            live_list.append(ASHPitem(
                name=link.get_text(),
                detailurl=link.get('href'),
                ashp_id = idnumber
            ))

    def _compare_previous(self):
        online_ids = [drug.ashp_id for drug in self.live_list]
        local_ids = [drug.ashp_id for drug in self.local_list]
        
        self.new_shortages = [x for x in self.live_list if x.ashp_id not in local_ids]
        self.resolved_shortages = [x for x in self.local_list if x.ashp_id not in online_ids]
        
    def update_db(self):
        db_path = config.DB_FILE
        database = ShortageDB(self, db_path)
        delete_ids = [item.ashp_id for item in self.resolved_shortages]
        for rem in delete_ids:
            for item in database:
                if item.ashp_id == rem:
                    del item
        add_drugs = [item for item in self.new_shortages]
        saving = []
        for item in database:
            saving.append({"ashp_id": item.ashp_id, "drugname": item.name},)
        for add in add_drugs:
            database.append({"ashp_id": add_drugs.ashp_id, "drugname": add_drugs.drugname})
        ShortageDB.store(saving)