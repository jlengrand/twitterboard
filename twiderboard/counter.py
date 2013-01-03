#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This part of the application is responsible for the calculation of statistics
that will be used in order to generate the leaderboards.
Whatever is in this file should:
- periodically poll the database, searching for non crawled elements
- extract the user from the elements together with the corresponding tag
- create a new entry with the user/hashtag couple if it doesnt exist yet.
- add a new point for this couple
- note the processed elements as crawled
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from datamodel import Base
from datamodel import Tweet

root = '/home/test/Documents/twiderboard'


class Counter():
    def __init__(self, engine_url):

        # creates engine, tries to create all the tables needed later on
        engine = create_engine(engine_url, echo=True)
        Base.metadata.create_all(engine)
        # initiates session to the database, tries to create proper session
        Session = sessionmaker(bind=engine)
        self.session = Session()  # Bridges class to db

    def count(self):
        """
        Every time is it called, perform a check of the database, and searches
        for elements that have not been crawled yet
        """
        query = self.session.query(Tweet).order_by(Tweet.id)
        #print query.all()
        #print query
        #query.all()
        for tweet in query:
            print tweet.hashtag, tweet.author

engine_url = 'sqlite:///twiderboard.db'
c = Counter(engine_url)
c.count()