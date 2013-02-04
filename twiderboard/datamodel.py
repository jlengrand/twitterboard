import re
import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import Index

from encodingUtils import EncodingUtils

Base = declarative_base()


class TrendyHashtag(Base):
    """
    Stores the list of hashtags that have been marked for tracking.
    Keeps history of all hashtags marked in the past, using an active boolean.
    Used for tracability and trendy hashtags sharing between Threads
    """
    __tablename__ = "trendy_hashtag"
    id = Column(Integer, primary_key=True)
    hashtag = Column(String(200))  # should begin with # is it is really a hashtag
    created = Column(DateTime)
    updated = Column(DateTime)  # used to track when is was last stopped/started
    active = Column(Boolean)  # Whether the hashtag is currently tracked or not.

    # places an index on hashtags
    __table_args__ = (Index('idx_hashtag', 'hashtag'), )

    def __init__(self, hashtag, active=True):
        self.hashtag = hashtag
        self.active = active

        self.created = datetime.datetime.now()
        self.updated = datetime.datetime.now()


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
    author = Column(String(200))  # name of the guy that tweeted
    hashtag = Column(String(200))  # name of the hashtag of the tweet
    created = Column(DateTime)  # date of creation of the member
    updated = Column(DateTime)  # date of last count update
    count = Column(Integer)  # Number of tweets for this couple author/hashtag

    # places an index on members, for a given hashtag
    __table_args__ = (Index('idx_member', 'author', 'hashtag'), )

    # places an index on members, to create leaderboards faster
    __table_args__ = (Index('idx_leader', 'hashtag', 'count', 'author'), )

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
    __tablename__ = "tweet"
    id = Column(Integer, primary_key=True)
    hashtag = Column(String(200))  # Hashtag that is tracked
    text = Column(String(200))  # Content of the tweet
    author = Column(String(200))  # name of the tweeter
    created = Column(String(200))  # FIXME: Change to date. Date at which message was tweeted
    inserted = Column(DateTime)  # Date at which tweet was saved in db
    crawled = Column(Boolean)  # Boolean whether or not tweet is in statistics already
    source = Column(String(200))  # Where tweet comes from

    # Boolean that is set to True if Tweet cannot be processed correctly
    invalid = Column(Boolean)

    def __init__(self, author, created, inserted, source, text):
        self.eu = EncodingUtils()  # used to switch to unicode

        self.author = self.eu.to_unicode(author)
        self.created = self.eu.to_unicode(created)
        self.crawled = False
        self.inserted = inserted
        self.source = self.eu.to_unicode(source)
        self.hashtag = self.eu.to_unicode('')
        self.text = self.eu.to_unicode(text)

        self.hashtags = self.extract_hashtags()

        self.invalid = False  # cannot be invalid by default

    def extract_hashtags(self):
        """
        Extracts all the hashtags that are present in the tweet
        FIXME: Problem here is that we lose lots of tags because they end/start
        with special characters!
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
            self.hashtag = self.eu.to_unicode(match[0])

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
            try:
                return "<%s('%s','%s', '%s')>" % (self.author.encode('utf-8'), self.created.encode('utf-8'), self.hashtag.encode('utf-8'), self.text.encode('utf-8'))
            except UnicodeDecodeError:
                return "Contains Unicode!!"
