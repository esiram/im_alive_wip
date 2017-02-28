
""" Note: triple (###) stand for TBD info/updates; double (##) stand for this is code to use later probably; single (#) and triple quotes stand for normal notes. """

### Correct later on as needed: in the schema.sql file I guessed on types, probably need to change many of the ones initially used


#ALL IMPORTS
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
#from .imalive import app


### should I create a separate .py or .ini file for configuration code? (see step 2 of flaskr ap)

#CONFIGURATION CODE
"""Loads default config and overrides config from environment variable."""
app = Flask(__name__)     # create app instance & initialize it
app.config.from_object(__name__)     # load config from this file, imalive.py

"""The below app.config.update(dict()) info needs better work... does it match up with imalive ap?"""
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'imalive.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
    ))
app.config.from_envvar('IMALIVE_SETTINGS', silent=True)

"""### Regarding DB path: should I make instance folders here (see Flaskr Step 2 sample) ALSO: see about the silent=TRUE/FALSE for the enviroment settings in step 2. ###"""

   
#FUNCTIONS TO CONNECT DB
def connect_db():
    """Connects to specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if none yet for current application context."""
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error): #note: if things go well the error parameter is None
    """Closes the database again at end of request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


#FUNCTIONS TO INITIALIZE DB
def init_db():
    """Opens file from resource folder."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    
@app.cli.command('initdb')  #flask creates an application context bound to correct application
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')



#VIEW FUNCTIONS
### TBD: how to redirect screens ###

### See step 6 in flaskr tutorial regarding hashing and salting passwords -- this still needs to happen. ###

### Question: may I have two lines of @app.route on top of the same definition (i.e. '/' and '/home')? ###

@app.route('/')
def home():
   """ Handles home screen (home.html). """
   ### needs future work here. ###
   return render_template('home.html')

#SURVIVOR VIEW FUNCTIONS
@app.route('/signup')
def signup_survivor():
    """ Handles survivor new accounts; adds info to db. """
    ### Needs lots of future work. ###
    return render_template('signup_survivor')


""" ### ES: can you make a login function that can be used for all users?  Basically, that you can invoke within the login_survior() function and the login_admin() function??? Basically: if admin return render_template ('login_admin.html') vs. if survivor return render_template ('login_survivor.html'). ### """
    
@app.route('/login_survivor', methods=['GET', 'POST'])
def login_survivor(): 
    """ Login for survivors checks username and password against configuration & sets logged_in key for session.  If user successfully logged in, the key sets to TRUE; else user gets redirected to home.html (aka home) screen."""
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = "Invalid username. Please try again."
        elif request.form['password'] != app.config['PASSWORD']:
            error = "Invalid password. Please try again."
        else:
            session['logged_in'] = True
            flash('You have successfully logged in.')
            return redirect(url_for('update_info'))
    # else: request.method == "GET":    
    return render_template('login_survivor.html', error=error)

@app.route('/logout')
def logout():
    """ Logs out all users (admin and survivors). """
    session.pop('logged_in', None)
    flash('You have logged out.')
    return redirect(url_for('home'))
    
        
# GENERAL USER QUERY VIEWS -- these users not logged in
@app.route('/search')
def search():
    """ Handles search.html screen -- eventual search query screen -- current db retrieval test page. """
    ### more work required here ###
    return render_template('search.html')

@app.route('/we_live')
def we_live():
    """ Handles we_live.html screen -- eventual "found" aka search answer screen -- current db. retrieval test page. """
    db = get_db()
    cur = db.execute('select familyName, personalName, originCountry, originCity, todayDate from table)survivors by familyName desc limit 5')
    table_survivors = cur.fetchall()
    return render_template('we_live.html', table_survivors=table_survivors)
    



        
        



   
