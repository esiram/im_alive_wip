#ALL IMPORTS
import os
import sqlite3 #I created a models.py file but need to think this through more 3-8-17es
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash



### Should I create a separate .py or .ini file for configuration code? (see step 2 of flaskr app model)

#CONFIGURATION CODE
"""Loads default config and overrides config from environment variable."""
app = Flask(__name__) # create app instance & initialize it  ##original code
app.config.from_object(__name__)     # load config from this file, imalive.py

#verify that the below info works for imalive; basically copied from flaskr example
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'imalive.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
    ))
app.config.from_envvar('IMALIVE_SETTINGS', silent=True)


#FUNCTIONS TO CONNECT DB
def connect_db():
   """Connects to specific database."""
   rv = sqlite3.connect(app.config['DATABASE']) 
   rv.row_factory = sqlite3.Row #this allows rows to be treated like dictionaries vs tuples
   return rv

def get_db():
    """Opens a new database connection if none yet for current application context."""
    if not hasattr(g, 'sqlite_db'):
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

def insertSurvivor():
    """For dynamic data entry."""
    familyname = familyname
    personalname = personalname
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO survivors (familyname, personalname) VALUES (?, ?)",                   (familyname, personalname))
    conn.commit()
#    conn.close() #do you want to close this?

def retrieveSurvivors():
    """For retrieval of survivor info from 'survivors' table.""" 
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT familyname, personalname FROM survivors")
    survivorList = cur.fetchall()
    conn.close()
    return survivorList
       

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

    


#VIEW FUNCTIONS
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

   
#SURVIVOR VIEW FUNCTIONS
@app.route('/signupSurvivor', methods = ['POST', 'GET'])
def signupSurvivor():
    """Handles survivor signup screen (signupSurvivor.html)."""
    render_template('signupSurvivor.html', error = None)
    while request.method == 'POST':
        familyname = request.form['familyname']
        personalname = request.form['personalname']
        error = None
        if familyname and personalname: #for now to keep simple
            insertSurvivor()
            return redirect(url_for("celebrate", personalname = personalname))
        else:
            error = "Not enough information to continue, please fill in asterisked/starred items."
            return render_template('signupSurvivor.html', error = error)
    else: #request.method == 'GET'
        return render_template('signupSurvivor.html', error = None)


    
@app.route('/celebrate', methods = ['GET']) # GET and POST method(s) needed or just GET?
def celebrate():
    """Handles the celebrate/end screen (celebrate.html)."""
    # personalname = "Esther" #personalname hardcoded for now
    # if request.method == 'POST':
    #     personalname = "POSTmethodTest" #personalname hardcoded for now
    # else:
    personalname = "Esther"  #request.form[personalname] didn't work here
    return render_template('celebrate.html', personalname = personalname)



@app.route('/loginSurvivor', methods = ['POST', 'GET'])
def loginSurvivor():
    """Handles survivor login to update information (loginSurvivor.html)."""
    return render_template('loginSurvivor.html')



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
            return redirect(url_for("celebrate", personalname = personalname))
        else:
            error = "Not enough information to continue; please provide both a family and a personal name. Thank you."
            return render_template('search.html', error = error, personalname = personalname, familyname = familyname)
    else: #request.method == 'GET'
        return render_template('search.html', error = None)
