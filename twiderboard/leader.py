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
    def __init__(self, hashtag=None, size=10):
        self.url = engine_url
        self.hashtag = hashtag
        self.size = size

        self.interval = 10
        self.leader_proc = RepeatingTimer(self.interval, self.leader_print)

    def start(self):
        """
        Starts counting new members periodically
        """
        self.leader_proc.start()

    def stop(self):
        """
        Stops counting new members periodically
        """
        self.leader_proc.stop()

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

    def get_hashtags():
        """
        Returns a list of all current tracked hashtags\
        TODO: Implement
        """

    def get_leaders(self):
        """
        Returns a list of the current leaders for the chosen hashtags.
        self.hashtag can be either the hashtag that has to be printed or None.
        If self.hashtag is None, the leaders for all current tracked hashtags will be outputed.


        The result will be a list of twitter usernames, with the current number
        of tweets containing the hashtag they sent.
        The list is of max size size, but can be smaller of even empty if no
        user has been detected yet.

        The result is of type :
        [[#hashtag1, [Leader1, Leader2, ...]],  [#hashtag2, [Leader1, Leader2, ...]]]
        #FIXME : Ugly and done in the train. Get back to this soon .
        """
        session = self.connect()
        leaders = []
        if self.hashtag is None:
            hashtags = self.get_hashtags()
            #TODO: Fill this
        else:
            l_query = session.query(Member).filter(Member.hashtag == self.hashtag).order_by(desc(Member.count))
            top_members = l_query.all()
            if self.size > 0:
                top_members = top_members[0:self.size]
            leaders.append([self.hashtag, top_members])

        return leaders


class DumbLeaderBoard(LeaderBoard):

    def __init__(self, hashtag, size=10):
        LeaderBoard.__init__(self, hashtag, size)

    def leader_print(self):
        """
        Periodically retrieves the leaders for the given hashtag
        and prints them out
        """
        leaders = self.get_leaders()
        self.print_leaders(leaders)

    # def get_leaders(self):
    #     """
    #     Returns the current leaders of the competition for the given hashtag
    #     The result will be a list of twitter usernames, with the current number
    #     of tweets containing the hashtag they sent.
    #     The list is of max size size, but can be smaller of even empty if no
    #     user has been detected yet.
    #     """
    #     session = self.connect()
    #     #l_query = session.query(Member).filter(Member.hashtag == self.hashtag).order_by(desc(Member.count))
    #     print self.hashtag
    #     l_query = session.query(Member).order_by(desc(Member.count))
    #     leaders = l_query.all()
    #     if self.size > 0:
    #         leaders = leaders[0:self.size]

    #     return leaders

    def print_leaders(self, leaders):
        """
        Dumps the list of leaders on the console
        leaders is of type :
        [[#hashtag1, [Leader1, Leader2, ...]],  [#hashtag2, [Leader1, Leader2, ...]]]
        """
        for hashtag, members in leaders:
            print "######### %s #########" % (hashtag)
            for member in members:
                print "%s - %d" % (member.author, member.count)

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
    l = DumbLeaderBoard("#nowplaying", 10)
    print "Press CTRL + C to stop application"
    l.start()
