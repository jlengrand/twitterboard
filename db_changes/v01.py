"""
Changes made between v00 and v01

Operation is :
- Add new column of type boolean and name invalid in Tweet table
"""
import sqlite3

db_name = '/home/jll/Documents/code/twitterboard/twiderboard.db'

con = sqlite3.connect(db_name)
c = con.cursor()
c.execute("ALTER TABLE tweets ADD COLUMN 'invalid' BOOLEAN")
con.commit()
c.close()

print "database updated to v01"