import re

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import DateTime

from encodingUtils import EncodingUtils

engine_url = "sqlite:///twiderboard.db"
Base = declarative_base()


class Tweet(Base):
    """
    Class that full =y represents a tweet as it is stored in the database.
    It is different from the structure that can be found in tweepy.
    """
    __tablename__ = "tweets"
    id = Column(Integer, primary_key=True)
    hashtag = Column(String)  # Hashtag that is tracked
    text = Column(String)  # Content of the tweet
    author = Column(String)  # name of the tweeter
    created = Column(String)  # FIXME: Change to date. Date at which message was tweeted
    inserted = Column(DateTime)  # Date at which tweet was saved in db
    crawled = Column(Boolean)  # Boolean whether or not tweet is in statistics already
    source = Column(String)  # Where tweet comes from

    def __init__(self, author, created, inserted, crawled, source, text):
        self.eu = EncodingUtils()  # used to switch to unicode
        print "IN"
        self.author = self.eu.to_unicode(author)
        self.created = self.eu.to_unicode(created)
        self.crawled = crawled
        self.inserted = inserted
        self.source = self.eu.to_unicode(source)
        self.hashtag = ''
        self.text = self.eu.to_unicode(text)

        self.hashtags = self.extract_hashtags()
        print self.hashtags

    def extract_hashtags(self):
        """
        Extracts all the hashtags that are present in the tweet
        """
        return re.findall(r"#(\w+)", self.text)

    def __repr__(self):
        return "<%s('%s','%s', '%s')>" % (self.author, self.created, self.hashtag, self.text)
