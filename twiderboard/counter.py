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

from utils.timing import RepeatingTimer
from data import debug
from data import engine_url

#import logging
import signal


class Counter():
    def __init__(self, engine_url):
        self.url = engine_url

        self.cpt = 0  # Used to force data flushing to db
        self.interval = 1  # repeats every second by default

        # element that repeats count method periodically
        self.count_unit = RepeatingTimer(self.interval, self.count)

    def connect(self):
        """
        Separated so that the method can be run in each created thread.
        Initiates connexion to the database and starts a Session to be used to query it.
        Returns the session used to communicate with the database
        """
        # creates engine, tries to create all the tables needed later on
        engine = create_engine(self.url, echo=debug)
        Base.metadata.create_all(engine)
        # initiates session to the database, tries to create proper session
        Session = sessionmaker(bind=engine)

        return Session()  # Bridges class to db

    def start(self):
        """
        Starts counting new members periodically
        """
        self.count_unit.start()

    def stop(self):
        """
        Stops counting new members periodically
        """
        self.count_unit.stop()

    def set_interval(self, interval):
        """
        Changes the frequency at which count is called
        """
        self.interval = interval

    def display_tweets(self):
        """
        debug

        Every time is it called, perform a check of the database, searches
        for elements that have not been crawled yet and displays them.
        """
        session = self.connect()
        query = session.query(Tweet).order_by(Tweet.id)
        for tweet in query:
            print tweet.hashtag, tweet.author

    def count(self):
        """
        Every time is it called, perform a check of the database, searches
        for elements that have not been crawled yet.
        They are then added to the members database.
        """
        print "((((((((((((((((((((((( COUNTING )))))))))))))))))))))))))))"

        session = self.connect()

        t_query = session.query(Tweet).filter(Tweet.crawled == False).order_by(Tweet.id)
        tweets = t_query.all()
        print "New counts to perform : %d" % (len(tweets))

        for tweet in tweets:
            try:
                t_hash = tweet.hashtag
                t_auth = tweet.author
                m_query = session.query(Member).filter(Member.author == t_auth).filter(Member.hashtag == t_hash)

                # Checking if we already have such a member
                reslen = len(m_query.all())
                if reslen == 1:
                    #print "I found a member. I have to update it"
                    self.update(session, m_query.first(), tweet)
                elif reslen == 0:
                    #print "I have to create a new member."
                    self.create(session, tweet)
                else:
                    #print "Error, can't get more than one member. Exiting"
                    raise ElementException  # FIXME : Take care

                self.flush(session)
            except ElementException:
                print "Exception on %s " % (tweet)

    def update(self, session, member, tweet):
        """
        Updates member values.
        Increments counter by 1, and changes updated field
        """
        if (member.has_author() and member.has_hashtag()):
            member.update()
            session.add(member)

            # sets tweet to crawled state
            tweet.crawled = True
            session.add(tweet)

            self.cpt += 1
        else:
            #print "Cannot update Member, Member is not valid"
            raise ElementException  # FIXME : Take care

    def create(self, session, tweet):
        """
        Creates a new Member using data from the given Tweet
        Called when no Member is found for the current
        author/hashtag couple.
        """
        if (tweet.has_author() and tweet.has_hashtag()):
            member = Member(tweet.author, tweet.hashtag, 1)
            session.add(member)

            # sets tweet to crawled state
            tweet.crawled = True
            session.add(tweet)

            self.cpt = 1
        else:
            #print "Cannot create Member, Tweet is not valid"
            raise ElementException  # FIXME : Take care

    def member_show(self, num=20):
        """
        debug

        Returns the number of Members in table
        """
        print "#########################################"
        session = self.connect()
        self.member_count()
        query = session.query(Member).order_by(Member.id).all()
        ptr = 0
        for q in query:
            ptr += 1
            if ptr < num:
                print q

    def member_count(self):
        """
        debug

        Returns the number of Members in table
        """
        session = self.connect()
        query = session.query(Member).order_by(Member.id).all()
        print "Members: %d" % (len(query))

    def flush(self, session):
        """
        Flushes data to db if enough data has to be updated

        FIXME: By not flushing every time, we might have doublons
        if the same guy tweets several times with the same flag
        """
        limit = 1
        if self.cpt >= limit:
            session.commit()  # force saving changes
            self.cpt = 0


class ElementException(Exception):
    """
    What else do !?
    """
    def __init__(self):
        Exception.__init__(self)
        # FIXME: Better printing at least


# ---------
def stop_handler(signal, frame):
    """
    Detects when the user presses CTRL + C and stops the count thread
    """
    global c
    c.stop()
    print "You stopped the counting!"


# registering the signal
signal.signal(signal.SIGINT, stop_handler)

# Initiates counter and starts it
c = Counter(engine_url)
c.start()
print "Press CTRL + C to stop application"
