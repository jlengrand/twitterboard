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

import data

import logging


class Counter():
    def __init__(self, engine_url):
        self.url = engine_url

        self.cpt = 0  # Used to force data flushing to db
        self.interval = 1  # repeats every second by default

        # sets up logger
        self.logger = self.setup_logger()

        # element that repeats count method periodically
        self.count_unit = RepeatingTimer(self.interval, self.count)

    def setup_logger(self):
        """
        Sets up logging capabilities. Defines precisely how and where logging
        information will be displayed and saved
        """
        my_logger = logging.getLogger("Counter")

        my_logger.setLevel(logging.ERROR)
        fh = logging.FileHandler(data.log_path)  # file part of logger
        fh.setLevel(logging.ERROR)

        #ch = logging.StreamHandler()  # console part of the logger
        #ch.setLevel(logging.DEBUG)

        my_logger.addHandler(fh)
        #my_logger.addHandler(ch)
        my_logger.info("########")   # Separate sessions

        return my_logger

    def connect(self):
        """
        Separated so that the method can be run in each created thread.
        Initiates connexion to the database and starts a Session to be used to query it.
        Returns the session used to communicate with the database
        """
        # creates engine, tries to create all the tables needed later on
        engine = create_engine(self.url, echo=data.debug)
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

    def display_tweets(self):
        """
        debug

        Every time is it called, perform a check of the database, searches
        for elements that have not been crawled yet and displays them.
        """
        session = self.connect()
        query = session.query(Tweet).order_by(Tweet.id)
        for tweet in query:
            self.logger.info(tweet.hashtag + " " + tweet.author)

    def count(self):
        """
        Every time is it called, perform a check of the database, searches
        for elements that have not been crawled yet.
        They are then added to the members database.
        """
        #print('.')
        self.logger.info("((((((((((((((((((((((() COUNTING )))))))))))))))))))))))))))")
        session = self.connect()

        t_query = session.query(Tweet).filter(Tweet.crawled == False).order_by(Tweet.id)
        tweets = t_query.all()
        self.logger.info("New counts to perform : %d" % (len(tweets)))
        # FIXME: This is blocking. It shouldnt!
        for tweet in tweets:
            try:
                t_hash = tweet.hashtag
                t_auth = tweet.author
                m_query = session.query(Member).filter(Member.author == t_auth).filter(Member.hashtag == t_hash)

                # Checking if we already have such a member
                reslen = len(m_query.all())
                if reslen == 1:
                    self.logger.info("Member found, updating. . .")
                    self.update(session, m_query.first(), tweet)
                elif reslen == 0:
                    self.logger.info("No member found, creating. . .")
                    self.create(session, tweet)
                else:
                    self.logger.error("ElementException :  More than one member found !")
                    raise ElementException  # FIXME : Take care
            except ElementException:
                self.invalidate(session, tweet)
                self.logger.error("ElementException :  Could not process %s !" % (tweet))

            self.commit_counts(session)

    def invalidate(self, session, tweet):
        """
        Invalidates a tweet so that it is not recrawled by the counter
        and can be verified later
        """
        tweet.invalid = True
        tweet.crawled = True
        session.add(tweet)

        self.cpt += 1  # indicates that we have a candidiate for the flushing

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
            self.logger.error("ElementException :  Cannot update Member, Member is not valid !")
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
            self.logger.error("ElementException :  Cannot create Member, Tweet is not valid !")
            raise ElementException  # FIXME : Take care

    def member_show(self, num=20):
        """
        debug

        Returns the number of Members in table
        """
        self.logger.info("#########################################")

        session = self.connect()
        self.member_count()
        query = session.query(Member).order_by(Member.id).all()
        ptr = 0
        for q in query:
            ptr += 1
            if ptr < num:
                self.logger.info(q)

    def member_count(self):
        """
        debug

        Returns the number of Members in table
        """
        session = self.connect()
        query = session.query(Member).order_by(Member.id).all()

        self.logger.info("Members: %d" % (len(query)))

    def commit_counts(self, session):
        """
        Commits data to db if enough data has to be updated

        FIXME: By not commiting every time, we might have duplicates
        if the same guy tweets several times with the same flag
        """
        #pass
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


# ---------
# def stop_handler(signal, frame):
#     """
#     Detects when the user presses CTRL + C and stops the count thread
#     """
#     global c
#     c.stop()
#     print "You stopped the counting!"


# # registering the signal
# signal.signal(signal.SIGINT, stop_handler)

# # Initiates counter and starts it
# c = Counter(engine_url)
# c.start()
# print "Press CTRL + C to stop application"
