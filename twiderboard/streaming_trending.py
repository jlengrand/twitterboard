#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.auth import BasicAuthHandler
from tweepy.auth import AuthHandler

from textwrap import TextWrapper

# to catch ctrl + c
import signal
import sys

# Go to http://dev.twitter.com and create an app.
# The consumer key and secret will be generated for you after

# After the step above, you will be redirected to your app's page.
# Create an access token under the the "Your access token" section

root = '/home/test/Documents/twiderboard/' # TODO: do that correctly in the future

class StreamWatcherListener(StreamListener):

    status_wrapper = TextWrapper(width=60, initial_indent='    ', subsequent_indent='    ')

    def __init__(self):
        StreamListener.__init__(self)

        self.twitlog_name = root + "twitlog.log"
        self.twitlog = open(self.twitlog_name, "w")  # erased each time we start

    def on_status(self, status):

        try:
            print self.status_wrapper.fill(status.text)
            print '\n %s  %s  via %s\n' % (status.author.screen_name, status.created_at, status.source)

            # extracting hastags
            res = re.findall(r"#(\w+)", status.text)
            hashs = ""
            for onehash in res:
                hashs += " " + onehash

            self.twitlog.write('\n %s  %s  via %s. Hashs = %s ' % (status.author.screen_name, status.created_at, status.source, hashs))

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


class StdOutListener(StreamListener):
    """ A listener handles tweets are the received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """

    def on_data(self, data):
        print data
        return True

    def on_error(self, status):
        print status


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
            file_name =  root + "oauth.keys"
            self.oauth_authenticate(file_name)
        else:
            file_name =  root + "basic.keys"
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


# class UpgradedStream(Stream):
#     def __init__(self, auth, listener, **options):
#         Stream.__init__(self, auth, listener, **options)
#         #registering signal
#         signal.signal(signal.SIGINT, self.signal_handler)
#         signal.pause()

#     def signal_handler(self, signal, frame):
#         """
#         Used to catch CTRL + C and exit in a clean way
#         """
#         print "You pressed CTRL + C"
#         self.disconnect()
#         sys.exit(0)

if __name__ == '__main__':
    # most trendy hashtags currently
    trendy = ["#smartiphone5BNOLotto", "#enkötüsüde", "#GiveMeThatGlobeIphone5", "#SilivriyeÖzgürlük", "#CiteNomesFeios",  "#121212concert", "#ItsNotCuteWhen", "#nowplaying", "#Blessed", "#breakoutartist"]
    andkey = " OR "

    l = StreamWatcherListener()
    myAuth = Authentification(oauth=True)

    #stream = UpgradedStream(myAuth.get_auth(), l)
    stream = Stream(myAuth.get_auth(), l)

    print "Trends streamed will be : "
    print trendy

    stream.filter(track=trendy)