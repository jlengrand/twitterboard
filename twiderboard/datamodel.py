from sql_alchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

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
    created = Column()  # TODO: Date at which was tweeted
    inserted = Column()  # TODO: date at which tweet was saved in db
    crawled = Column()  # TODO: Boolean whether or not tweet is in statistics already
    source = Column(String)  # Where tweet comes from

    def __init__():
        pass