"""
Contains all code needed to serve files on the webserver.
"""
from flask import Flask
from flask import render_template

app = Flask(__name__)


@app.route("/")
def webprint():
    #return "Hello World!"
    return render_template('index.html')

if __name__ == "__main__":
    app.run()
