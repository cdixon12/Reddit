#!/usr/bin/env python3

# Chase Dixon  5/3/23

import re
import os
import requests
from db_manager import Base
from sqlalchemy import Column, Integer, String, Boolean

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)

    # add all of the Columns for the settings the program will have
    sub_regex = Column(String)
    title_regex = Column(String)
    comment_regex = Column(String)
    sub_num = Column(Integer)
    title_num = Column(Integer)
    comment_num = Column(Integer)
    sub_reverse = Column(Boolean)
    title_reverse = Column(Boolean)
    comment_reverse = Column(Boolean)
    title_attr = Column(String)
    comment_attr = Column(String)
    username = Column(String)
    password = Column(String)
    # 14 LOC ???

    def __init__(self, sub_regex='.*', title_regex='.*', comment_regex='.*',
                        sub_num=25, title_num=25, comment_num=25,
                        sub_reverse=False, title_reverse=False, comment_reverse=False,
                        title_attr='score', comment_attr='score', username='', password=''):

       # set all of the attributes for the Settings object 
        self.sub_regex = sub_regex
        self.title_regex = title_regex
        self.comment_regex = comment_regex
        self.sub_num = sub_num
        self.title_num = title_num
        self.comment_num = comment_num
        self.sub_reverse = sub_reverse
        self.title_reverse = title_reverse
        self.comment_reverse = comment_reverse
        self.title_attr = title_attr
        self.comment_attr = comment_attr
        self.username = username
        self.password = password
       # 11 LOC

    def __repr__(self) -> str:
        return super().__repr__()

class Subreddit(Base):
    __tablename__ = 'subreddits'
    id = Column(Integer, primary_key=True)

    # add a column for the subreddit URL
    # 1 LOC
    url = Column(String)

    def __init__(self, url: str, user: User) -> None: # 2 LOC
        # set the two Subreddit attributes
        self.url = url
        self.user = user

    def scrape(self) -> None: # 4 LOC
        # scrape the Subreddit URL and instantiate a list of Post objects
        headers = {'user-agent': 'reddit-{}'.format(os.environ.get('USER', 'cse-30332-sp23'))}
        response = requests.get(self.url, headers=headers)
        self.posts = response.json()['data']['children']
        self.posts = sorted(self.posts, key=lambda x: x['data'][self.user.title_attr])      # sort based on title_attr
        self.post_list = [Post(p['data'], self.user) for p in self.posts]  # create post object
        self.filtered_posts = []

        if self.user.title_reverse == True:
            self.post_list.reverse()

    def display(self, loc: int, titles: bool = False) -> tuple: # 8 LOC
        # return a tuple with the subreddits URL and a list of Posts you want to

        # display (it's possible this may be an empty list)
        # if titles is True, then scrape the subreddit
        self.filtered_posts = [] 
        if titles == True:
            try:
                self.scrape()
            except:
                self.post_list = []
                self.filtered_posts = []
                
            l = 0
            for p in self.post_list:

                if p.filter(p.title, False):
                    
                    if l != int(self.user.title_num):
                        l += 1
                        self.filtered_posts.append(p)
                    else:
                        break

        return(self.url, self.filtered_posts)   #tuple
        

        
    def filter(self) -> bool: # 3 LOC
        # Check if the URL of the subreddit matches the regex for subreddits
        if re.match(self.user.sub_regex, self.url):
            return True

        return False

    def __repr__(self) -> str:
        return super().__repr__()

class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    # add a column for the post URL
    # 1 LOC
    url = Column(String)

    def __init__(self, data, user) -> None: # 6 LOC
        # set the Posts attributes from the passed in data
        # such as title, selftext, and name
        self.data = data
        self.user = user
        self.title = data['title']
        self.text = data['selftext']
        self.counter = 0
        self.url = data['url'] + '.json'


    def scrape(self) -> None: # 3 LOC
        # scrape the Post's URL
        headers = {'user-agent': 'reddit-{}'.format(os.environ.get('USER', 'cse-30332-sp23'))}
        response = requests.get(self.url, headers=headers)
        self.comments = response.json()[1]['data']['children']

        if self.user.comment_reverse == True:
            self.comments.reverse()

    def display(self, loc: int, comments: bool = False) -> tuple: # 10 LOC
        # return a tuple containing the posts title and a list of all Comments to display
        # it's possible the comment list may be empty
        # if comments is true, then scrape the post

        comment_list = []
        if comments == True:
            try:
                self.scrape()
            except:
                self.comments = {} 
            
            for comment in self.comments:
                try:
                    if self.filter(comment['data']['body'], True):
                        comment_list.append(self.display_comment_tree(comment, 0))
                        self.counter += 1

                    if self.counter == int(self.user.comment_num):
                        break
                except:
                    print('No body for this comment') 

        return (self.title, comment_list)


    def display_comment_tree(self, reply_dict: dict, depth: int) -> str: #12 LOC
        # return a single comment object, whose children attribute contains the comments children
        
        try:
            if self.filter(reply_dict['data']['body'], True):
                c = Comment(reply_dict['data']['name'], reply_dict['data']['created_utc'], reply_dict['data']['body'], reply_dict['data'][self.user.comment_attr])
            # Base Case
            if reply_dict['data']['replies'] == '':
                return c

        except:
            return Comment('', '', '', '')

        for child in reply_dict['data']['replies']['data']['children']:     # recursively call function on each child comment
            c.children.append(self.display_comment_tree(child, depth + 1))

        return c


    def filter(self, item, comments: bool = False) -> bool: # 6 LOC
        # return true or false depending on whether or not the item matches its regex
        if comments == True:    # comment filter
            if re.match(self.user.comment_regex, item):
                return True

        else:                   # title filter
            if re.match(self.user.title_regex, item):
                return True

        return False
        
    def __repr__(self) -> str:
        return super().__repr__()

class Comment():
    def __init__(self, user, time, body, attr):
        # initialize the attributes of the comment class
        # additionally add a list of child comments as well
        self.user = user
        self.time = time
        self.body = body
        self.attr = attr
        self.children = []


