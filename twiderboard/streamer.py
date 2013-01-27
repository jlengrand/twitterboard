#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy.auth import BasicAuthHandler
from tweepy.auth import AuthHandler

from tweepy import Stream

from datamodel import Base
from datamodel import Tweet
from datamodel import Member
from datamodel import TrendyHashtag

from counter import ElementException

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from encodingUtils import EncodingUtils

import data


class StreamSaverListener(StreamListener):
    """
    Stream that will save each tweet it receives into a database
    to be reused later
    """
    def __init__(self, hashtags, session, engine):
        StreamListener.__init__(self)
        self.cpt = 0   # FIXME: test if useful
        self.eu = EncodingUtils()

        self.hashtags = self.format_hashtags(hashtags)
        self.session = session  # bridge to the db
        self.engine = engine

    def on_status(self, status):
        """
        Each time a tweet is received
        """
        tweet = Tweet(status.author.screen_name,
            status.created_at,
            datetime.datetime.now(),
            status.source,
            status.text)

        tweet.get_main_tag(self.hashtags)  # FIXME: should be part of the init, shouldn t it ?

        #self.session.add(tweet)
        # here i should update members now.
        self.update_members(tweet)

        self.cpt += 1

        if self.cpt >= 1:
            self.session.commit()  # force saving changes
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

    def update_members(self, tweet):
        """
        Updates the member table using the last tweet received.
        If Member already exists and has already used the hashtag, its counter will be incremented.
        If member doesnt exist yet for the hashtag, it will be created.
        """
        auth = tweet.author
        hasht = tweet.hashtag
        m_query = self.session.query(Member).filter(Member.author == auth).filter(Member.hashtag == hasht)

        reslen = len(m_query.all())
        if reslen >= 1:
            print "Error: Duplicate members found."
        elif reslen == 0:
            print "No member found, creating"
            self.create_member(tweet)
        else:  # reslen = 1
            print "Member found, updating"
            self.update_member(m_query.first())

    def create_member(self, tweet):
        """
        Creates a new Member using data from the given Tweet
        Called when no Member is found for the current
        author/hashtag couple.
        """
        if (tweet.has_author() and tweet.has_hashtag()):
            member = Member(tweet.author, tweet.hashtag, 1)
            self.session.add(member)

        else:
            self.logger.error("ElementException :  Cannot create Member, Tweet is not valid !")
            raise ElementException  # FIXME : Take care

    def update_member(self, member):
        """
        Updates member values.
        Increments counter by 1, and changes updated field
        """
        if (member.has_author() and member.has_hashtag()):
            member.update()
            self.session.add(member)

        else:
            self.logger.error("ElementException :  Cannot update Member, Member is not valid !")
            raise ElementException  # FIXME : Take care


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
            file_name = data.oauth_keys
            self.oauth_authenticate(file_name)
        else:
            file_name = data.basic_keys
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
        session, engine = self.connect()

        h_query = session.query(TrendyHashtag).filter(TrendyHashtag.active == True)
        hashtags = h_query.all()

        trendy = []
        for hashtag in hashtags:
            trendy.append(hashtag.hashtag)

        session.close()
        engine.dispose()

        return trendy

    def start(self):
        session, engine = self.connect()

        if len(self.trendy) > 0:
            listener = StreamSaverListener(self.trendy, session, engine)

            self.stream = Stream(self.auth.get_auth(), listener)
            print self.trendy
            self.stream.filter(track=self.trendy, async=True)
        else:
            print "No hashtag to track!"

    def stop(self):
        if self.stream is not None:
            self.stream.listener.session.close()  # FIXME: this is awful as hell
            self.stream.listener.engine.dispose()  # FIXME: Create twitterstream inherited from stream. Override disconnect
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
        session, engine = self.connect()

        h_query = session.query(TrendyHashtag)
        all_hashs = h_query.all()
        all_names = [h.hashtag for h in all_hashs]

        #FIXME: Do that correctly ! This si soooooo ugly!
        # check if hashtag to add is already present but inactive
        if hashtag in all_names:
            for h in all_hashs:
                if h.hashtag == hashtag:  # there but not active
                    if h.active == False:
                        h.active = True
                        h.updated = datetime.datetime.now()
                        trendy_hashtag = h
                    else:
                        #do nothing, already there and active !
                        return
        else:  # new hashtag to be created
            trendy_hashtag = TrendyHashtag(hashtag)

        session.add(trendy_hashtag)

        self.commit_hashtag(session)

        self.trendy.append(hashtag)  # appends in list

        session.close()

        self.restart()
        engine.dispose()

    def commit_hashtag(self, session):
        """
        Takes care of errors that can happen if database if locked when session is commited
        """
        session.commit()  # sends to db

    def remove_hashtag(self, hashtag):
        """
        FIXME: Check if starts with #
        Removes hashtag to the list of trendy hashtag to be listened to.
        The streaming connexion is reinitialized to take the new filter into
        account.
        """
        session, engine = self.connect()

        if hashtag in self.trendy:
            # removes hashtag from active list
            h_query = session.query(TrendyHashtag).filter(TrendyHashtag.hashtag == hashtag).filter(TrendyHashtag.active == True)
            hashtags = h_query.all()

            if 0 == len(hashtags) > 1:
                print "Hashtag not recorded in database!"
            else:
                # sets hashtag as inactive and updates date
                trendy_hashtag = hashtags[0]
                trendy_hashtag.active = False
                trendy_hashtag.updated = datetime.datetime.now()

                session.add(trendy_hashtag)
                self.commit_hashtag(session)

                # removes from list
                self.trendy.remove(hashtag)

        session.close()

        self.restart()
        engine.dispose()

    def connect(self):
        """
        Separated so that the method can be run in each created thread.
        Initiates connexion to the database and starts a Session to be used to query it.
        Returns the session used to communicate with the database
        """
        # creates engine, tries to create all the tables needed later on
        engine = create_engine(self.engine_url, echo=data.debug)
        Base.metadata.create_all(engine)
        # initiates session to the database, tries to create proper session
        Session = sessionmaker(bind=engine)

        return Session(), engine  # Bridges class to db
