from flask import Flask, jsonify, render_template, request
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from datamodel import TrendyHashtag

#hash_value=3
url = "mysql+mysqldb://root:test@localhost:3306/twiderboard_test"
# creates engine, tries to create all the tables needed later on
engine = create_engine(url, echo=False)
# initiates session to the database, tries to create proper session
Session = sessionmaker(bind=engine)
session = Session()


@app.route('/nb_trendy')
def nb_trendy():
    query = session.query(func.count(TrendyHashtag.id))
    val = query.first()[0]
    return jsonify(hashs=val)


@app.route('/_add_numbers')
def add_numbers():
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    return jsonify(result=a + b)


@app.route('/')
def index():
    #return render_template('index_dyn.html')
    return render_template('statistics.html')

if __name__ == '__main__':
    app.run()
