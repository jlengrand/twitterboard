import re
import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import DateTime

from encodingUtils import EncodingUtils

engine_url = "sqlite:///twiderboard.db"
Base = declarative_base()


class Member(Base):
    """
    Represents an entry in a leaderboard.
    An entry in the leaderboard is fully represented by the name of the poster,
    the number of tweets he posted and the corresponding hashtag
    Some more information can be stored in the db, such as the last update
    or the creation date
    """
    __tablename__ = "member"
    id = Column(Integer, primary_key=True)
    author = Column(String)  # name of the guy that tweeted
    hashtag = Column(String)  # name of the hashtag of the tweet
    created = Column(DateTime)  # date of creation of the member
    updated = Column(DateTime)  # date of last count update
    count = Column(Integer)  # Number of tweets for this couple author/hashtag

    def __init__(self, author, hashtag, count=0):
        self.author = author
        self.hashtag = hashtag
        self.created = datetime.datetime.now()
        self.updated = datetime.datetime.now()
        self.count = count

    def increment(self):
        """
        Increments the count value
        """
        self.count += 1

    def update(self):
        self.increment()
        self.updated = datetime.datetime.now()

    def has_author(self):
        """
        Returns True if author is not empty or null
        """
        return (len(self.author) != 0 and self.author is not None)

    def has_hashtag(self):
        """
        Returns True if hashtag is not empty or null
        """
        return (len(self.hashtag) != 0 and self.hashtag is not None)

    def __repr__(self):
        return "<%s('%s' on'%s' last '%s') count: %s>" % (self.author, self.hashtag, self.created, self.updated, self.count)


class Tweet(Base):
    """
    Class that fully represents a tweet as it is stored in the database.
    It is different from the structure that can be found in tweepy
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

        self.author = self.eu.to_unicode(author)
        self.created = self.eu.to_unicode(created)
        self.crawled = crawled
        self.inserted = inserted
        self.source = self.eu.to_unicode(source)
        self.hashtag = ''
        self.text = self.eu.to_unicode(text)

        self.hashtags = self.extract_hashtags()

    # BETTER, but see how it works
    def extract_hashtags(self):
        """
        Extracts all the hashtags that are present in the tweet
        """
        return set(part[:] for part in self.text.split() if part.startswith('#'))
        #return re.findall(r"#(\w+)", self.text)

    def get_main_tag(self, trendy):
        """
        Given a list of tracked hashtag, defines the most important one
        """
        in_hashs = [i.lower() for i in self.hashtags]
        trend_hashs = [i.lower() for i in trendy]
        match = [i for i in in_hashs if i in trend_hashs]
        if len(match) != 0:
            self.hashtag = match[0]

    def has_author(self):
        """
        Returns True if author is not empty or null
        """
        return (len(self.author) != 0 and self.author is not None)

    def has_hashtag(self):
        """
        Returns True if hashtag is not empty or null
        """
        return (len(self.hashtag) != 0 and self.hashtag is not None)

    def __repr__(self):
            # FIXME: Solve this!
            try:
                return "<%s('%s','%s', '%s')>" % (self.author.encode("UTF-8"), self.created, self.hashtag.encode("UTF-8"), self.text.encode("UTF-8"))
            except UnicodeDecodeError:
                return "Contains Unicode!!"
