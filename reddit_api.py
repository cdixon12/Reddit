#!/usr/bin/env python3

# Chase Dixon 5/3/23

from flask import Flask ,request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from db_manager import db_session
from reddit_classes import User, Subreddit, Post
from flask_bootstrap import Bootstrap
from markupsafe import Markup
from flaskext.markdown import Markdown

app = Flask(__name__)
Bootstrap(app)
Markdown(app)

user = None
subs = None

def check_globals() -> None: # 8 LOC
    global user
    global subs

    # create a default User object if it doesn't exist
    if user == None:
        user = User()

    # get the subreddit objects from the database and add the User object
    # if the subreddit objects don't already exist
    all_subs = Subreddit.query.all()
    for sub in all_subs:
        sub.user = user 
    subs = []
    count = 0
    for sub in all_subs:            # set settings object for each subreddit object
        if sub.filter():            # filter subreddit urls
            subs.append(sub)
            count += 1
        if count == int(user.sub_num):
            break

    if user.sub_reverse == True:
        subs.reverse()


@app.route('/', methods=['GET','POST'])
def display_subreddits() -> str: # 6 LOC
    check_globals()
    if request.method == "POST":
        try:
            nav_filter = '.*' + request.form['nav_filter'] + '.*'
        except:
            nav_filter = None

        if nav_filter != None:
            user.sub_regex = nav_filter

    check_globals()

    # return a template displaying all of the subreddits and links to their posts
    return render_template('subreddits.html', subs=subs)

@app.route('/<int:sub_id>/', methods=['GET', 'POST'])
def display_post_titles(sub_id: int) -> str: # 2 LOC
    check_globals()
    # handles navbar filter
    if request.method == "POST":
        try:
            nav_filter = '.*' + request.form['nav_filter'] + '.*'
        except:
            nav_filter = None

        if nav_filter != None:
            user.title_regex = nav_filter

    # return a template displaying all of the posts and links to their comments
    curr_sub = sub_id
    p = subs[sub_id].display(sub_id, True)
    return render_template('posts.html', posts=p[1], sub_id=curr_sub)

@app.route('/<int:sub_id>/<int:post_id>/', methods=['GET', 'POST'])
def display_post_comments(sub_id: int, post_id: int) -> str: # 6 LOC
    check_globals()
    # handles navbar filter
    if request.method == "POST":
        try:
            nav_filter = '.*' + request.form['nav_filter'] + '.*'
        except:
            nav_filter = None

        if nav_filter != None:
            user.comment_regex = nav_filter

    # return a template displaying all of the comments
    subs[sub_id].display(sub_id, True)      #  need in order to run scrape function
    post = subs[sub_id].filtered_posts[post_id]
    c = post.display(post_id, True)
    return render_template('comments.html', comments=c[1], title=c[0])


@app.route('/settings/', methods=['GET', 'POST'])
def settings() -> None: # 12 LOC
    # if there is a POST request update the User object with the new items
    # if there is a GET request, and the user is not logged in, redirect them
    # to the login page, otherwise display the settings page for the user
    check_globals()
    if request.method == "POST":
    
        user.sub_regex = request.form['sub_regex'] 
        user.title_regex = request.form['title_regex'] 
        user.comment_regex = request.form['comment_regex'] 
        user.sub_num  = int(request.form['sub_num'])
        user.title_num  = int(request.form['title_num'])
        user.comment_num = int(request.form['comment_num']) 
        user.title_attr = request.form['title_attr'] 
        user.comment_attr = request.form['comment_attr']
        
        if request.form['sub_reverse'] == 'True':
            user.sub_reverse = True
        else:
            user.sub_reverse = False

        if request.form['title_reverse'] == 'True':
            user.title_reverse = True
        else:
            user.title_reverse = False

        if request.form['comment_reverse'] == 'True':
            user.comment_reverse = True
        else:
            user.comment_reverse = False

         
    elif request.method == "GET" and user.username == '':
        return render_template('login.html', user=user )

    db_session.add(user) 
    db_session.commit() 
    return render_template('settings.html', user=user)
    

@app.route('/login/', methods=['GET', 'POST'])
def login() -> None: #10 LoC
    # if there is a POST request, log the user in and load their User object from the DB 
    # and redirect to the index page
    check_globals()
    global user

    if request.method == "POST":
        q = User.query.all()
        new_user = True
        for obj in q:
            if request.form['username'] == obj.username and request.form['password'] == obj.password:
                new_user = False
                user = obj
                print('welcome back')
                break  
        if new_user:
            new = User()
            new.username = request.form['username']
            new.password = request.form['password']
            user = new
            print('new user added')
        db_session.add(user)
        db_session.commit()

        return redirect('/', code=302)

    # if there is a GET request, return the login template
    return render_template('login.html')

    
@app.teardown_appcontext
def shutdown_session(exception=None): #4 LoC
    # save the users settings to the database
    db_session.commit()
    db_session.remove()


if __name__=='__main__':
    app.run(host='0.0.0.0', port=9054) 
