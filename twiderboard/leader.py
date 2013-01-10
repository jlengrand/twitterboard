#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This part of the application is responsible for generating and displaying the
leaderboard for selected hastags.

This module should not write or modify the database in any way, but only
consult it and extract useful information from it.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc

from datamodel import Base
from datamodel import Member

from data import debug
from data import engine_url

from time import sleep

class LeaderBoard():

    def __init__(self, hashtag, size=10):
        self.url = engine_url
        self.hashtag = hashtag
        self.size = size

    def connect(self):
        """
        Initiates connexion to the database and starts a Session to be used to
        query it.
        Returns the session used to communicate with the database
        """
        # creates engine, tries to create all the tables needed later on
        engine = create_engine(self.url, echo=debug)
        Base.metadata.create_all(engine)
        # initiates session to the database, tries to create proper session
        Session = sessionmaker(bind=engine)

        return Session()  # Bridges class to db

    def get_leaders(self):
        """
        Returns the current leaders of the competition for the given hashtag
        The result will be a list of twitter usernames, with the current number
        of tweets containing the hashtag they sent.
        The list is of max size size, but can be smaller of even empty if no
        user has been detected yet.
        """
        session = self.connect()
        l_query = session.query(Member).filter(Member.hashtag == self.hashtag).order_by(desc(Member.count))
        leaders = l_query.all()
        if self.size > 0:
            leaders = leaders[0:self.size]

        return leaders

    def print_leaders(self, leaders):
        """
        Dumps the list of leaders on the console
        """
        print "#########"
        for leader in leaders:
            print "%s - %d" % (leader.author, leader.count)

l = LeaderBoard("#nowplaying", 10)
for i in range(20):
    leaders = l.get_leaders()
    l.print_leaders(leaders)
    sleep(5)

