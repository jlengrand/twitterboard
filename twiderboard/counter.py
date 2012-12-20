#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This part of the application is responsible for the calculation of statistics
that will be used in order to generate the leaderboards.
Whatever is in this file should:
- periodically poll the database, searching for non crawled elements
- extract the user from the elements together with the corresponding tag
- create a new entry with the user/hashtag couple if it doesnt exist yet.
- add a new point for this couple
- note the processed elements as crawled
"""

root = '/home/test/Documents/twiderboard'

class Counter():
    def __init__(self):
