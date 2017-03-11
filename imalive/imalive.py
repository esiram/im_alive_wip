### ALL IMPORTS ###
import os
import sqlite3 
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash


### CONFIGURATION CODE ###
"""Loads default config and overrides config from environment variable."""

app = Flask(__name__)                # create app instance & initialize it
app.config.from_object(__name__)     # load config from this file, imalive.py

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'imalive.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
    ))
app.config.from_envvar('IMALIVE_SETTINGS', silent=True)



### DATABASE FUNCTIONS ###
#FUNCTIONS TO CONNECT DB
def connect_db():
   """Connects to specific database."""
   rv = sqlite3.connect(app.config['DATABASE'])
   rv.row_factory = sqlite3.Row #this allows rows to be treated like dictionaries vs tuples
   return rv

def get_db():
    """Opens a new database connection if none yet for current application context."""
    if not hasattr(g, 'sqlite_db'):  #store db in a global variable 'g'
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):          #if things go well the error parameter is None
    """Closes the database again at end of request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

        
#FUNCTIONS TO UTILIZE DB
def create_table():
    """To create table 'survivors' if table doesn't exist."""
    conn = connect_db() #connection
    cur = conn.cursor() #cursor
    cur.execute('CREATE TABLE IF NOT EXISTS survivors(familyname TEXT, personalname TEXT, signupdate TIMESTAMP)')
       

#FUNCTIONS TO INITIALIZE DB
def init_db():
    """Opens file from resource folder."""
    db = get_db()
    c = db.cursor()   #db.cursor() used in flaskr tutorial rather than c
    with app.open_resource('schema.sql', mode='r') as f:
       c.executescript(f.read())
    db.commit()
    
@app.cli.command('initdb')  #flask creates an application context bound to correct application
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

    
    
### VIEW FUNCTIONS ###
#GENERAL VIEW FUNCTIONS
@app.route('/', methods = ['POST', 'GET'])
@app.route('/home', methods = ['POST', 'GET'])
def home():
   """ Handles home screen (home.html). """
   render_template('home.html')
   while request.method == 'POST':
       doWhat = request.form['doWhat']
       if doWhat == "search":
           return redirect(url_for("search"))
       elif doWhat == "signup":
           return redirect(url_for("signupSurvivor"))
       else:
           return redirect(url_for("loginSurvivor"))
   else:
       return render_template('home.html')


@app.route('/celebrate', methods = ['GET', 'POST'])
def celebrate():
    """Handles the celebrate screen (celebrate.html)."""
#    personalname = request.form['personalname']###NOT WORKING
    return render_template('celebrate.html', personalname = "Esther", signupDate = "3-7-17")

    
   
#SURVIVOR VIEW FUNCTIONS
@app.route('/signupSurvivor', methods = ['GET', 'POST'])
def signupSurvivor():
    """Handles survivor signup screen (signupSurvivor.html)."""
    render_template('signupSurvivor.html', error = None)
    while request.method == 'POST':
       error = None
       familyname = request.form['familyname']
       personalname = request.form['personalname']
       password = request.form['password']
       if familyname and personalname and password: #for now to keep simple
          db = get_db()
          db.execute('INSERT INTO survivors (familyname, personalname, password) VALUES (?, ?, ?)',
                     [request.form['familyname'], request.form['personalname'], request.form['password']])
          db.commit()
          return redirect(url_for("celebrate", personalname = personalname))
       else:
           error = "Not enough information to continue, please fill in asterisked/starred items."
           return render_template('signupSurvivor.html', error = error)
    else: #request.method == 'GET'
       return render_template('signupSurvivor.html', error = None)


@app.route('/loginSurvivor', methods = ['GET', 'POST'])
def loginSurvivor():
    """Handles survivor login to update information (loginSurvivor.html)."""
    render_template('loginSurvivor.html')    
    error = None
    if request.method == 'POST':
       if request.form['personalname'] != app.config['PERSONALNAME']: #see app.config info in flask docs
          error = 'Invalid personal name.'
          render_template('loginSurvivor.html', error = error)  
       elif request.form['familyname'] != app.config['FAMILYNAME']:
          error = 'Invalid family name.'
          render_template('loginSurvivor.html', error = error)  
       elif request.form['password'] != app.config['PASSWORD']:
          error = 'Invalid password.'
          render_template('loginSurvivor.html', error = error)  
       else:
          return render_template('signupSurvivor.html')  #this may need a different redirect



#SEARCH VIEW FUNCTIONS
@app.route('/search', methods = ['POST', 'GET'])
def search():
    """Handles the search index screen (search.html)."""
    render_template('search.html', error = None)
    while request.method == 'POST':
        familyname = request.form['familyname']
        personalname = request.form['personalname']
        error = None
        if familyname and personalname: #for now to keep simple
           db = get_db()
           db.execute('SELECT * FROM survivors WHERE familyname = ?', [request.form['familyname']])#, request.form['personalname']]) ###this not working 3-9-17
           if familyname is None:
              error = "No such survivor with that name has enrolled with I'mAlive."
              return render_template('search.html', error = error)
           else:
              return redirect(url_for("celebrate", personalname = personalname))
        else:
            error = "Not enough information to continue; please provide both a family and a personal name. Thank you."
            return render_template('search.html', error = error, personalname = personalname, familyname = familyname)
    else: #request.method == 'GET'
        return render_template('search.html', error = None)
