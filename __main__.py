import logging
import os
from datetime import date

from reddit.redditapi import NewPost
from database import ShortageDB
from database.database import ASHPitem, ChangeTrk

changes = ChangeTrk()

logging.basicConfig(level=logging.INFO, format='%(asctime)s : %(levelname)s : %(message)s')
logging.info(f'Found {len(changes.new_shortages)} new shortages, and {len(changes.resolved_shortages)} shortages removed...')

if changes.new_shortages:
    logging.info('Now attempting to post new drug shortages to r/drugshortages...')
    for new_item in changes.new_shortages:
        post = redditapi.NewPost.new_short(new_item)
    logging.info('Finished posting new drug shortages to r/drugshortages!')

if changes.resolved_shortages:
    logging.info('Now attempting to post resolved drug shortages to r/drugshortages...')
    for new_item in changes.resolved_shortages:
        post = redditapi.NewPost.new_rmv(new_item)
    logging.info('Finished posting resolved drug shortages to r/drugshortages!')