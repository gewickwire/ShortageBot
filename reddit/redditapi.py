import praw

from config import config
from database.database import ASHPitem


class NewPost:
    def __init__(self, druginfo: ASHPitem):
        #creates a new reddit post. drugname parameter is the short drug.
        self.druginfo = druginfo
        self.session = praw.Reddit(
            client_id=config['REDDIT_KEY'],
            client_secret=config['REDDIT_SECRET'],
            user_agent=config['REDDIT_USERAGENT'],
            username=config['REDDIT_USERNAME'],
            password=config['REDDIT_PASSWORD'],
        )
        self.subforum = self.session.subreddit(config['SUBREDDIT'])
        
    def new_short(self):
        #if a new shortage, set variables for shortage post
        submission_text = f'A shortage of **{self.druginfo.name}** has been added to the the ASHP \
        list of drug shortages. Please visit [the details page]({self.druginfo.link}) for more information.*'
        self.flair = config['SHORTAGE_FLAIR_ID']
        post_post(submission_text)

    def new_rmv(self):
        #if a new removal, set variables for removal post
        submission_text = f'The previously reported drug shortage for **{self.druginfo.name}** has been \
        removed from the ASHP shortages list. Please note that this does not necessarily mean that the \
        product is widely available, just that there is no longer a national/widespread shortage.*'
        self.flair = config['REMOVAL_FLAIR_ID']
        post_post(submission_text)

    def post_post(text):
        self.subforum.submit(
            title=self.druginfo.name,
            selftext=text,
            flair_id=self.flair,
            send_replies=False,
        )