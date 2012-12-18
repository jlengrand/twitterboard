#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import datetime

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy.auth import BasicAuthHandler
from tweepy.auth import AuthHandler

from textwrap import TextWrapper

from datamodel import Base
from datamodel import Tweet

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Go to http://dev.twitter.com and create an app.
# The consumer key and secret will be generated for you after

# After the step above, you will be redirected to your app's page.
# Create an access token under the the "Your access token" section

root = '/home/test/Documents/twiderboard/'  # TODO: do that correctly


class StreamSaverListener(StreamListener):
    """
    Stream that will save each tweet it receives into a database
    to be reused later
    """
    def __init__(self, hashtags, engine_url):
        StreamListener.__init__(self)
        self.hashtags = hashtags
        # creates engine, initiates session, tries to create tables
        engine = create_engine(engine_url, echo=True)
        Base.metadata.create_all(engine)

        # Defines a sessionmaker that will be used to connect to the DB
        Session = sessionmaker(bind=engine)
        self.session = Session()  # bridge to the db

    def on_status(self, status):
        """
        Each time a tweet is received
        """
        try:
            #tries to save tweet in database

            main_hash = self.extract_hashtag(status.text)

            tweet = Tweet(status.author.screen_name,
                status.created_at,
                datetime.now(),
                False,
                status.source,
                main_hash,
                status.text)

            self.session.add(tweet)

        except:
            # Catches any unicode errors while printing to console
            # and just ignore them to avoid breaking application.
            #print "Unicode Error ! %s" % (status)
            pass

    def on_error(self, status_code):
        print 'An error has occured! Status code = %s' % status_code
        return True  # keep sstream alive

    def on_timeout(self):
        print 'Snoozing Zzzzzz'

    def extract_hashtag(self, text):
        """
        Extracts the hashtag that trigerred the tweet
        to be streamed
        """
        # extracting hastags
        res = re.findall(r"#(\w+)", text)
        hashs = ""
        for onehash in res:
            hashs += " " + onehash

        # getting main hash
        for one_hash in hashs:
            if one_hash in self.hashtags:
                return one_hash

        # No hash found
        return None

class StreamWatcherListener(StreamListener):

    status_wrapper = TextWrapper(width=60,
                                                        initial_indent=' ',
                                                        subsequent_indent='  ')

    def __init__(self):
        StreamListener.__init__(self)

        self.twitlog_name = root + "twitlog.log"
        # erased each time we start
        self.twitlog = open(self.twitlog_name, "w")

    def on_status(self, status):

        try:
            #print self.status_wrapper.fill(status.text)
            #print "STATUS : %s" % (status.text)
            print "FILL : %s" % (self.status_wrapper.fill(status.text))
            #print '\n %s  %s  via %s\n' % (status.author.screen_name,
            #  status.created_at,
            # status.source)

            # extracting hastags
            res = re.findall(r"#(\w+)", status.text)
            hashs = ""
            for onehash in res:
                hashs += " " + onehash

            self.twitlog.write('\n %s  %s  via %s. Hashs = %s ' %
                (status.author.screen_name, status.created_at,
                    status.source, hashs))

        except:
            # Catch any unicode errors while printing to console
            # and just ignore them to avoid breaking application.
            #print "Unicode Error ! %s" % (status)
            pass

    def on_error(self, status_code):
        print 'An error has occured! Status code = %s' % status_code
        return True  # keep stream alive

    def on_timeout(self):
        print 'Snoozing Zzzzzz'


class Authentification(AuthHandler):
    """
    Extracts private connexion information to authenticate to Twitter.
    Avoids having to disclose private information on the web.
    """

    def __init__(self, oauth=False):
        """
        Creates authentication depending on user request.
        Default is basic auth (user/pass), but oauth is also possible
        """
        self.auth = None

        if oauth:
            file_name = root + "oauth.keys"
            self.oauth_authenticate(file_name)
        else:
            file_name = root + "basic.keys"
            self.basic_authenticate(file_name)

    def basic_authenticate(self, file_name):
        """
        Creates an Authhandler using Basic method
        """
        try:
            with open(file_name) as f:
                cred = f.readline() .split(',')
        except IOError:
            print "Error  : Authentication file not found"

        if len(cred) != 2:
            print "Error : Expecting to retrieve 2 values"
        else:
            #username, password
            self.auth = BasicAuthHandler(cred[0], cred[1])

    def oauth_authenticate(self, file_name):
        """
        Creates an Authhandler using OAuth method
        Also sets access token.
        Needs both consumer key and secret and
        access token and token_secret
        """
        try:
            with open(file_name) as f:
                consumer = f.readline() .rstrip('\n').split(',')
                access = f.readline() .split(',')
        except IOError:
            print "Error  : Authentication file not found"

        if len(consumer) + len(access) != 4:
            print "Error : Expecting to retrieve 4 values"
        else:
            #consumer_key, consumer_secret
            self.auth = OAuthHandler(consumer[0], consumer[1])
            #access_token, access_token_secret
            self.auth.set_access_token(access[0], access[1])

    def get_auth(self):
        return self.auth
