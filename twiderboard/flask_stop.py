from flask import Flask

from streamer import HashtagLogger
import data
from flask import g


app = Flask(__name__)
h = HashtagLogger(data.engine_url, oauth=data.oauth)
h.start()


@app.route('/')
def index():
    return "Hi there!!!"


@app.route('/add_hashtag')
def add_hashtag():
    hashtag = h.add_hashtag('plop')
    return hashtag


@app.route('/remove_hashtag')
def remove_hashtag():
    hashtag = h.remove_hashtag('plop')
    return hashtag


@app.route('/stop')
def stop():
    h.stop()
    return h.stream.engine


def run():
    app.run()

if __name__ == '__main__':
    app.run(debug=True)