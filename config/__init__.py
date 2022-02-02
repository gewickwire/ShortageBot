#reddit account config

import json
import os
from pathlib import Path

config = {
    'SECRET_KEY': 'dev',
    'PREFERRED_URL_SCHEME': 'http',
    'REDDIT_KEY': '',
    'REDDIT_SECRET': '',
    'REDDIT_USERAGENT': 'python:com.example.shortagebot:v1.0.0 (by /u/Berchanhimez)',
    'REDDIT_USERNAME': '',
    'REDDIT_PASSWORD': '',
    'SHORTAGE_FLAIR_ID': '',
    'REMOVAL_FLAIR_ID': '',
    'SUBREDDIT': '',
    'DB_FILE': 'database\shortages.json',
}