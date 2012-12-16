from sqlalchemy import create_engine
from sqlalchemy.orm import mapper
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey


class User(object):
    def __init__(self, name, fullname, password):
        self.name = name
        self.fullname = fullname
        self.password = password

        def __repr__(self):
            return "<User('%s','%s', '%s')>" % (self.name, self.fullname, self.password)



if __name__ == '__main__':

    engine = create_engine('sqlite:///:memory:', echo=True)
    metadata = MetaData()
    users_table = Table('users', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('fullname', String),
    Column('password', String)
    )


    # safe to call multiple times
    metadata.create_all(engine)

    #maps table to class
    mapper(User, users_table)