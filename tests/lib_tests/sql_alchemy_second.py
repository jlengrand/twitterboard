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
    engine_url = 'sqlite:///twiderboard_test.db'

    engine = create_engine(engine_url, echo=True)

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

    print ed_user == our_user

    # we can add multiple elements
    flo = User('Flo', 'Florian', 'hehe')
    session.add_all([
        User('Mouton', 'Julien', 'mimi'),
        User('Coco', 'Coralie', 'bleble'),
        flo])

    #we can hard change data
    ed_user.password = 'r;oidgud'
    print session.dirty  # objects that changed
    print session.new  #  pending objects    print '#######'    print '#######'



    # this needs ressources to the db. Should be done only when needed to save ressources
    session.commit()  # force saving changes

    # rolling back changes
    ed_user.name = 'Joe'
    fake_user = User('Fake', 'User', 'None')
    session.add(fake_user)

    #querying the session shows that they re  flushed into the current transaction
    print session.query(User).filter(User.name.in_(['Fake', 'Joe'])).all()
    session.rollback()  # reverting changes

    # checking everything correctly reverted
    print ed_user.name
    print flo in session
    print ed_user

    print session.query(User).filter(User.name.in_(['No', 'fakeuser'])).all()


    # querying
    print '#######'
    print "Querying : "
    print '#######'

    # using db syntax
    print
    for instance in session.query(User).order_by(User.id):
        print instance.name, instance.password

    print ''
    # but also works using ORM syntax
    for name, password in session.query(User.name, User.password):
        print name, password

    # limit and offset can be used. Easiest way is with python slices
    for u in session.query(User).order_by(User.id)[1:3]:
        print u


    # there are two way to use filter :
    # filter_by, using keyword arguments
    for name in session.query(User.name).filter_by(fullname='Florian'):
        print name
    # or filter, using level class attributes and python operators
    for name, in session.query(User.name).filter(User.fullname=='Florian'):
        print name

    # most of the time, a query returns a query object which allows making series
    for user in session.query(User).filter(User.name=='No').filter(User.fullname=='tysurikat'):
        print user