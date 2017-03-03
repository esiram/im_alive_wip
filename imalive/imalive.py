
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

@app.route('/')
@app.route('/home')
def home():
   """ Handles home screen (home.html). """
   return render_template('home.html')


#SURVIVOR VIEW FUNCTIONS
@app.route('/signupSurvivor')
def signupSurvivor():
    """Handles survivor signup screen (signupSurvivor.html)."""
    return render_template('signupSurvivor.html')

@app.route('/celebrate')
def celebrate():
    """Handles the celebrate/end screen (celebrate.html)."""
    return render_template('celebrate.html', name = "Esther" ) #personalname but hardcoding now

@app.route('/loginSurvivor')
def loginSurvivor():
    """Handles survivor login to update information (loginSurvivor.html)."""
    return render_template('loginSurvivor.html')


#SEARCH VIEW FUNCTIONS
@app.route('/search')
def search():
    """Handles the search index screen (search.html)."""
    return render_template('search.html')
