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
from datamodel import Member

root = '/home/test/Documents/twiderboard'


class Counter():
    def __init__(self, engine_url):

        # creates engine, tries to create all the tables needed later on
        engine = create_engine(engine_url, echo=True)
        Base.metadata.create_all(engine)
        # initiates session to the database, tries to create proper session
        Session = sessionmaker(bind=engine)
        self.session = Session()  # Bridges class to db

    def display(self):
        """
        Every time is it called, perform a check of the database, searches
        for elements that have not been crawled yet and displays them.
        """
        query = self.session.query(Tweet).order_by(Tweet.id)
        #print query.all()
        #print query
        #query.all()
        for tweet in query:
            print tweet.hashtag, tweet.author

    def count(self):
        """
        Every time is it called, perform a check of the database, searches
        for elements that have not been crawled yet.
        They are then added to the members database.
        """
        t_query = self.session.query(Tweet).filter(Tweet.crawled == False).order_by(Tweet.id)
        tweet = t_query[0]
        if True:
            t_hash = tweet.hashtag
            t_auth = tweet.author
            print "###"
            print t_auth, t_hash
            debug = self.session.query(Member).all()
            print "''''''''''''''''''''''"
            for d in debug:
                print d.author, d.hashtag
            m_query = self.session.query(Member).filter(Member.author == t_auth).filter(Member.hashtag == t_hash)

            # Checking if we already have such a member
            reslen = len(m_query.all())
            if reslen == 1:
                print "I found a member. I have to update it"
            elif reslen == 0:
                print "I have to create a new member."
                self.create(tweet)
            else:
                print "Error, can't get more than one member. Exiting"
                raise Exception

    def create(self, tweet):
        """
        Creates a new Member using data from the given Tweet
        Called when no Member is found for the current
        author/hashtag couple.
        """
        if (tweet.has_author() and tweet.has_hashtag()):
            member = Member(tweet.author, tweet.hashtag)
        else:
            print "Cannot create Member, Tweet is not valid"
            raise Exception

        self.session.add(member)

        cpt = 1

        # trying to flush if needed
        if cpt >= 1: # FIXME: Raise limit later on
            self.session.commit()  # force saving changes
            print "Commiting"
            cpt = 0

    def member_count(self):
        """
        Returns the number of Members in table
        """
        query = self.session.query(Member).order_by(Member.id).all()
        print "Members: %d" % (len(query))

engine_url = 'sqlite:///twiderboard.db'
c = Counter(engine_url)
c.count()
c.member_count()