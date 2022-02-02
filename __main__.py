import logging
import os
from datetime import date

from reddit.redditapi import NewPost
from database import ShortageDB
from database.database import ASHPitem, ChangeTrk

def __init__(self):
    global new_shortages
    self.new_shortages = []
    global resolved_shortages
    self.resolved_shortages = []

changes = ChangeTrk()

num_new = len(new_shortages)
print(num_new)
num_old = len(resolved_shortages)


logging.basicConfig(level=logging.INFO, format='%(asctime)s : %(levelname)s : %(message)s')
logging.info('Found '+str(num_new)+' new shortages, and '+str(num_old)+' shortages were removed...', )

if num_new != 0:
    logging.info('Now attempting to post new drug shortages to r/drugshortages...')
    for new_item in new_shortages:
        post = redditapi.NewPost.new_short(new_item)
    logging.info('Finished posting new drug shortages to r/drugshortages!')

if num_old != 0:
    logging.info('Now attempting to post resolved drug shortages to r/drugshortages...')
    for new_item in resolved_shortages:
        post = redditapi.NewPost.new_rmv(new_item)
    logging.info('Finished posting resolved drug shortages to r/drugshortages!')