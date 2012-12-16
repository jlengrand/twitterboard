from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import create_engine


from sqlalchemy.orm import sessionmaker

# User now derives from Base, so that the mapping can be done at once
Base = declarative_base()
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    password = Column(String)

    def __init__(self, name, fullname, password):
        self.name = name
        self.password = password
        self.fullname = fullname

    def __repr__(self):
        return "<User('%s','%s', '%s')>" % (self.name, self.fullname, self.password)

if __name__ == '__main__':
    engine = create_engine('sqlite:///twiderboard.db', echo=True)

    Base.metadata.create_all(engine)
    # Defines a sessionmaker that will be used to create connections to the DB
    Session = sessionmaker(bind=engine)
    #Session = sessionmaker()

    ## Starts interacting with the DB
    session = Session()

    ed_user = User('No', 'tysurikat', 'blabla')
    session.add(ed_user)
    #no SQL issued yet, status is PENDING, will be sent next flushed

    our_user = session.query(User).filter_by(name='No').first()
    print our_user

