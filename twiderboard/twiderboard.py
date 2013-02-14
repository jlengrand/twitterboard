"""
Top level application that will start the streamer and the API.
"""

from flask_app import app

class Twiderboard():
    def __init__(self):
        app.run()
        print "coucou"
