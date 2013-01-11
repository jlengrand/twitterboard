#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy.auth import BasicAuthHandler
from tweepy.auth import AuthHandler

from tweepy import Stream

from data import debug


from datamodel import Base
from datamodel import Tweet

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from encodingUtils import EncodingUtils

from data import root


class StreamSaverListener(StreamListener):
    """
    Stream that will save each tweet it receives into a database
    to be reused later
    """
    def __init__(self, hashtags, engine_url):
        StreamListener.__init__(self)
        self.cpt = 0   # FIXME: test if useful
        self.eu = EncodingUtils()

        self.hashtags = self.format_hashtags(hashtags)

        # creates engine, initiates session, tries to create tables
        engine = create_engine(engine_url, echo=debug)
        Base.metadata.create_all(engine)

        # Defines a sessionmaker that will be used to connect to the DB
        Session = sessionmaker(bind=engine)
        self.session = Session()  # bridge to the db

    def on_status(self, status):
        """
        Each time a tweet is received
        """
        tweet = Tweet(status.author.screen_name,
            status.created_at,
            datetime.datetime.now(),
            status.source,
            status.text)

        tweet.get_main_tag(self.hashtags)

        #print tweet.hashtag.encode('utf-8')
        #sys.exit(0)

        self.session.add(tweet)
        self.cpt += 1

        # trying to flush if needed
        if self.cpt >= 10:
            self.session.commit()  # force saving changes
            #print (".")
            self.cpt = 0

    def on_error(self, status_code):
        print 'An error has occured! Status code = %s' % status_code
        return True  # keeps stream alive

    def on_timeout(self):
        print 'Snoozing Zzzzzz'

    def on_delete(self):
        return False

    def format_hashtags(self, hashs):
        """
        Returns the same list of hashtags in unicode format
        """
        return [self.eu.to_unicode(has) for has in hashs]


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


#--------------------------
class HashtagLogger():
    def __init__(self, engine_url, oauth=True):
        self.engine_url = engine_url
        self.trendy = []
        self.oauth = oauth  # Boolean defining whether we use oauth or not

        self.stream = None

        self.auth = Authentification(oauth=self.oauth)


    def start(self):
        if len(self.trendy) > 0:
            listener = StreamSaverListener(self.trendy, self.engine_url)

            self.stream = Stream(self.auth.get_auth(), listener)
            print self.trendy
            self.stream.filter(track=self.trendy, async=True)
        else:
            print "No hashtag to track!"

    def stop(self):
        if self.stream is not None:
            self.stream.disconnect()

    def add_hashtag(self, hashtag):
        """
        FIXME: Check if starts with #
        Adds hashtag to the list of trendy hashtag to be listened to.
        Hashtag is not added if already present.

        The streaming connexion is reinitialized to take the new filter into
        account.
        """
        if hashtag not in self.trendy:
            self.trendy.append(hashtag)

        self.stop()
        self.start()

    def remove_hashtag(self, hashtag):
        """
        FIXME: Check if starts with #
        Removes hashtag to the list of trendy hashtag to be listened to.
        The streaming connexion is reinitialized to take the new filter into
        account.
        """
        if hashtag in self.trendy:
            self.trendy.remove(hashtag)

        self.stop()
        self.start()
