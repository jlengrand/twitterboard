#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This part retrieves data that is inputed in the console and transforms
into commands that will trigger actions on the twiderboard
"""
import signal
import sys

from data import engine_url

from leader import LeaderBoard
from counter import Counter
from streamer import HashtagLogger


class Trigger():
    def __init__(self):
        # registering the signal to stop command line
        signal.signal(signal.SIGINT, self.stop_handler)

        # starting all services
        # Streamer
        print "streamer"
        self.h = HashtagLogger(engine_url, oauth=True)
        self.h.start()

        #Counter
        print "counter"
        self.c = Counter(engine_url)
        self.c.start()

        # FIXME: Must create a wrapper to display them all periodically here
        # LeaderBoard
        # self.l = LeaderBoardAll()
        # self.l.start()

        print "Command Line utility started:"
        print "Press CTRL + C to stop application"
        while True:
            raw_input(">")

    def stop_handler(self, signal, frame):
        """
        Detects when the user presses CTRL + C and stops the count thread
        """
        print ""
        print "Stopping Streamer"
        self.h.stop()
        print "Stopping Counter"
        self.c.stop()
        #print "Stopping LeaderBoard"
        #self.l.stop()
        print "Stopping Command Line"
        sys.exit(0)

Trigger()