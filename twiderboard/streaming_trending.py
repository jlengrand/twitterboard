#!/usr/bin/python
# -*- coding: utf-8 -*-
import signal

from tweepy import Stream

from streamer import StreamSaverListener
from streamer import Authentification

from data import engine_url

# most trendy hashtags currently
trendy = ["#smartiphone5BNOLotto", "#enkötüsüde", "#GiveMeThatGlobeIphone5", "#SilivriyeÖzgürlük", "#CiteNomesFeios",  "#121212concert", "#ItsNotCuteWhen", "#nowplaying", "#Blessed", "#breakoutartist"]
print "Trends streamed will be : "
print trendy


# ---------
def stop_handler(signal, frame):
    """
    Detects when the user presses CTRL + C and stops the count thread
    """
    global stream
    # should be some kind of stream.stop() here
    stream.disconnect()
    print "You just closed the stream!"

# registering the signal
signal.signal(signal.SIGINT, stop_handler)


l = StreamSaverListener(trendy, engine_url)
myAuth = Authentification(oauth=True)

stream = Stream(myAuth.get_auth(), l)
stream.filter(track=trendy)  # I need this to become a thread

print "Press CTRL + C to stop application"
