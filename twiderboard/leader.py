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

from utils.timing import RepeatingTimer

import signal


class LeaderBoard():

    def __init__(self, hashtag, size=10):
        self.url = engine_url
        self.hashtag = hashtag
        self.size = size

        self.interval = 2   # Number of seconds between each leaderboard display

        self.leader_unit = RepeatingTimer(self.interval, self.leaderprint)

    def start(self):
        """
        Starts counting new members periodically
        """
        self.leader_unit.start()

    def stop(self):
        """
        Stops counting new members periodically
        """
        self.leader_unit.stop()

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

    def leaderprint(self):
        """
        Periodically retrieves the leaders for the given hashtag
        and prints them out
        """
        leaders = self.get_leaders()
        self.print_leaders(leaders)

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

# ---------
def stop_handler(signal, frame):
    """
    Detects when the user presses CTRL + C and stops the count thread
    """
    global l
    l.stop()
    print "You stopped the leaderboard printing!"

if __name__ == '__main__':
    # registering the signal
    signal.signal(signal.SIGINT, stop_handler)

    # Initiates LeaderBoard and starts it
    l = LeaderBoard("#nowplaying", 10)
    print "Press CTRL + C to stop application"
    l.start()
