#!/usr/bin/python
# -*- coding: utf-8 -*-

from tweepy import Stream

from streamer import StreamWatcherListener
from streamer import Authentification


# most trendy hashtags currently
trendy = ["#smartiphone5BNOLotto", "#enkötüsüde", "#GiveMeThatGlobeIphone5", "#SilivriyeÖzgürlük", "#CiteNomesFeios",  "#121212concert", "#ItsNotCuteWhen", "#nowplaying", "#Blessed", "#breakoutartist"]
andkey = " OR "

l = StreamWatcherListener()
myAuth = Authentification(oauth=True)

stream = Stream(myAuth.get_auth(), l)

print "Trends streamed will be : "
print trendy

stream.filter(track=trendy)
