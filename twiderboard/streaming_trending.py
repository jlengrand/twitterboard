#!/usr/bin/python
# -*- coding: utf-8 -*-
import signal

from streamer import HashtagLogger

from data import engine_url

# most trendy hashtags currently
#trendy = ["#smartiphone5BNOLotto", "#enkötüsüde", "#GiveMeThatGlobeIphone5", "#SilivriyeÖzgürlük", "#CiteNomesFeios",  "#121212concert", "#ItsNotCuteWhen", "#nowplaying", "#Blessed", "#breakoutartist"]
#print "Trends streamed will be : "
#print trendy

def stop_handler(signal, frame):
    """
    Detects when the user presses CTRL + C and stops the count thread
    """
    global stream
    h.stop()
    print "You just closed the stream!"

# registering the signal
signal.signal(signal.SIGINT, stop_handler)

h = HashtagLogger(engine_url, "#nowplaying", oauth=True)
h.start()
print "Press CTRL + C to stop application"
