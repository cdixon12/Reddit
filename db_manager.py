#!/usr/bin/env python3

# Chase Dixon 5/3/23

import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

#create an engine for your DB using sqlite and storing it in a file named reddit.sqlite
engine = create_engine("sqlite:///reddit.sqlite")


db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False))

Base = declarative_base()
Base.query = db_session.query_property()

def init_db(): # 15 LOC
    '''Create the database and fill it with the first 1000 SFW Subreddits

    Args:
        None

    Returns:
        None
    '''

    # import your classes that represent tables in the DB and then create_all of the tables
    from reddit_classes import User, Subreddit, Post
    Base.metadata.create_all(bind=engine)

    # read in the subreddit lists from the given CSV and add the first 1000 SFW subreddits to your database by creating Subreddit objects
    subs = []
    with open('sub_info.csv', mode='r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            subs.append(row)

    user = User()
    sub_list = []   # list of subreddit objects which creates columns
    count = 0
    for s in subs: 
        if 'false' in s[2]:
            sub_list.append(Subreddit('https://www.reddit.com/r/' + s[1] + '/.json', user))
            count += 1
        if count == 1000:
            break
 
    for obj in sub_list:    # add each subreddit object to the db
        db_session.add(obj)

    # save the database
    db_session.commit()



