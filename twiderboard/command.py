#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This part retrieves data that is inputed in the console and transforms
into commands that will trigger actions on the twiderboard
"""
import signal
import sys

from data import engine_url

from counter import Counter
from streamer import HashtagLogger


class Trigger():
    def __init__(self):
        # registering the signal to stop command line
        signal.signal(signal.SIGINT, self.stop_handler)

        # starting all services
        # Streamer
        print "Starting streamer"
        self.h = HashtagLogger(engine_url, oauth=True)
        self.h.start()

        #Counter
        print "Starting counter"
        self.c = Counter(engine_url)
        self.c.start()

        # FIXME: Must create a wrapper to display them all periodically here
        # LeaderBoard
        # self.l = LeaderBoardAll()
        # self.l.start()

        print "Command Line utility started:"
        print "Press CTRL + C to stop application"
        print "type h, help or ? to get a list of possible commands"
        while True:
            res = raw_input(">")
            self.parse(res)

    def parse(self, comm):
        """
        Parses the command input by the user
        and triggers the corresponding action
        """
        word = comm.lower()
        if word in ["h", "help", "?"]:
            self.help()
        else:
            if word.startswith("add #"):
                hashtag = word.replace("add ", "")
                self.h.add_hashtag(hashtag)
            elif word.startswith("rm #"):
                hashtag = word.replace("rm ", "")
                self.h.remove_hashtag(hashtag)
            else:
                print "Unrecognized command"

    def help(self):
        """
        Prints Help message in command line
        """
        print "######"
        print "add [hashtag] : adds hashtag to list of interest hashtags "
        print "rm [hashtag] : removes hashtag from list of interest hashtags "
        print
        print "WARNING: hashtag always starts with #!"
        print "######"

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