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
from datamodel import TrendyHashtag

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from encodingUtils import EncodingUtils

from data import root


class StreamSaverListener(StreamListener):
    """
    Stream that will save each tweet it receives into a database
    to be reused later
    """
    def __init__(self, hashtags, session):
        StreamListener.__init__(self)
        self.cpt = 0   # FIXME: test if useful
        self.eu = EncodingUtils()

        self.hashtags = self.format_hashtags(hashtags)
        self.session = session  # bridge to the db

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
        self.oauth = oauth  # Boolean defining whether we use oauth or not
        self.auth = Authentification(oauth=self.oauth)
        self.stream = None

        self.trendy = self.load_hashtags()

    def load_hashtags(self):
        """
        Creates list of current trendy hashtags by loading
        all active hashtags from database
        """
        session = self.connect()

        h_query = session.query(TrendyHashtag).filter(TrendyHashtag.active == True)
        hashtags = h_query.all()

        trendy = []
        for hashtag in hashtags:
            trendy.append(hashtag.hashtag)

        return trendy

    def start(self):
        session = self.connect()

        if len(self.trendy) > 0:
            listener = StreamSaverListener(self.trendy, session)

            self.stream = Stream(self.auth.get_auth(), listener)
            print self.trendy
            self.stream.filter(track=self.trendy, async=True)
        else:
            print "No hashtag to track!"

    def stop(self):
        if self.stream is not None:
            self.stream.disconnect()

    def restart(self):
        self.stop()
        self.start()

    def add_hashtag(self, hashtag):
        """
        FIXME: Check if starts with #
        Adds hashtag to the list of trendy hashtag to be listened to.
        Hashtag is not added if already present.

        The streaming connexion is reinitialized to take the new filter into
        account.
        """
        session = self.connect()

        if hashtag not in self.trendy:
            # saves to db
            trendy_hashtag = TrendyHashtag(hashtag)
            session.add(trendy_hashtag)
            session.commit()  # sends to db

            self.trendy.append(hashtag)  # appends in list
            session.commit()

        self.restart()

    def remove_hashtag(self, hashtag):
        """
        FIXME: Check if starts with #
        Removes hashtag to the list of trendy hashtag to be listened to.
        The streaming connexion is reinitialized to take the new filter into
        account.
        """
        session = self.connect()

        if hashtag in self.trendy:
            # removes hashtag from active list
            h_query = session.query(TrendyHashtag).filter(TrendyHashtag.hashtag == hashtag).filter(TrendyHashtag.active == True)
            hashtags = h_query.all()

            if 0 == len(hashtags) > 1:
                print "Hashtag not recorded in database!"
            else:
                # removes from database
                trendy_hashtag = hashtags[0]
                trendy_hashtag.active = False
                trendy_hashtag.updated = datetime.datetime.now()

                session.add(trendy_hashtag)
                session.commit()

                # removes from list
                self.trendy.remove(hashtag)

        self.restart()

    def connect(self):
        """
        Separated so that the method can be run in each created thread.
        Initiates connexion to the database and starts a Session to be used to query it.
        Returns the session used to communicate with the database
        """
        # creates engine, tries to create all the tables needed later on
        engine = create_engine(self.engine_url, echo=debug)
        Base.metadata.create_all(engine)
        # initiates session to the database, tries to create proper session
        Session = sessionmaker(bind=engine)

        return Session()  # Bridges class to db