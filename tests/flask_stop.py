import time
from multiprocessing import Process
from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    return "Hi there!!!"


def run():
    app.run()

if __name__ == '__main__':
    app.debug = True
    print "starting process"
    server = Process(target=run)
    server.start()

    print "sleeping"
    time.sleep(5)

    print "ending process"
    server.terminate()
    server.join()

    print "bye..."
