### ALL IMPORTS ###
import os
import sqlite3
import datetime #for date stamp -- TO BE USED WITH DB ITEMS; not used as of 3/17/17
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
   rv.row_factory = sqlite3.Row           #this allows rows to be treated like dictionaries vs tuples
   return rv

def get_db():
    """Opens a new database connection if none yet for current application context."""
    if not hasattr(g, 'sqlite_db'):       #store db in a global variable 'g'
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):                      #if things go well the error parameter is None
    """Closes the database again at end of request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

        
#FUNCTIONS TO UTILIZE DB
def create_table():
    """To create table 'survivors' if table doesn't exist."""
    conn = connect_db()                   #connection
    cur = conn.cursor()                   #cursor (TBD: see init_db 'c' for cursor: determine if a general cursor object for the entire app should get made)
    cur.execute('CREATE TABLE IF NOT EXISTS survivors(familyname TEXT, personalname TEXT, signupdate TIMESTAMP)')
       

#FUNCTIONS TO INITIALIZE DB
def init_db():
    """Opens file from resource folder."""
    db = get_db()
    c = db.cursor()                         #db.cursor() used in flaskr tutorial rather than c (TBD: does this duplicate the create_table 'cur' variable? Can you simplify?)
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
   render_template('home.html', error = None)
   error = None
   while request.method == 'POST':     #should doWhat have a not null value????-ES 3/15/17
       doWhat = request.form['doWhat']
       if doWhat == "search":
           return redirect(url_for("search"))
       elif doWhat == "signup":
           return redirect(url_for("signupSurvivor"))
       elif doWhat == "login":
           return redirect(url_for("loginSurvivor"))
       else: #if nothing chosen but submit/enter button hit (i.e. doWhat = None); THIS DOESN'T WORK! Currently an error at redirections/rendering 'home.html'-es3/17/17
           return render_template('home.html', error = "TESTING WHICH ERROR MSG: Please select from one of the options.  Thank you.")
   else:    #request.method == 'GET'
      # error = "Please select from one of the options.  Thank you."
       return render_template('home.html')#, error = error)

#@app.route('/celebrate/<personalname>', methods = ['GET', 'POST']) #not pulling dynamic stuff into URL - Es 3/13/17
@app.route('/celebrate', methods = ['GET', 'POST'])
def celebrate():
    """Handles the celebrate screen (celebrate.html)."""
    if 'personalname' in session:                                                        #this pulls name dynamically into template, URL not showing yet as of 3/13/17
       return render_template('celebrate.html', personalname = session['personalname'], message = session['message'])  #this pulls name dynamically as of 3/13/17
    else:
       return render_template('celebrate.html', personalname = "EstherTester", signupDate = "TesterDateToday")

    
   
#SURVIVOR VIEW FUNCTIONS
@app.route('/signupSurvivor', methods = ['GET', 'POST'])
def signupSurvivor():
    """Handles survivor signup screen (signupSurvivor.html)."""
    render_template('signupSurvivor.html', error = None)
    while request.method == 'POST':
       error = None
       message = ""
       
       #form inputs:
       familyname = request.form['familyname']
       personalname = request.form['personalname']
       #additionalname = request.form['additionalname']
       gender = request.form['gender']  ##### as of 3/15/17: if this field empty, website has error msg not made by me.-ES
       #age = request.form['age']
       #year = request.form['year']
       #month = request.form['month']
       #day = request.form['day']
       #country = request.form['country']
       #city = request.form['city']
       #county = request.form['county']
       #village = request.form['village']
       #other = request.form['other']
       #sos = request.form['sos']
       #otherSOS = request.form['otherSOS']
       password = request.form['password']   #####  WORK ON HASHING and SALTING AT LATER DATE
       #password2 = request.form['password2'] ### if password2 == password:... else: error
       
       if familyname and personalname and password: #for now to keep simple
          db = get_db()
          if gender: #until I figure out how to do this w/o multiple lines like this -ES3/15/17:
              db.execute('INSERT INTO survivors (familyname, personalname, gender, password) VALUES (?, ?, ?, ?)',
                         [request.form['familyname'], request.form['personalname'], request.form['gender'], request.form['password']])
          else:   
              db.execute('INSERT INTO survivors (familyname, personalname, password) VALUES (?, ?, ?)',
                         [request.form['familyname'], request.form['personalname'], request.form['password']])
         # db.execute('INSERT INTO survivors (familyname, personalname, additionalname, gender, age, year, month, day, country, city, county, village,
         #                                    other, sos, otherSOS, password) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
         #                                    [request.form['familyname'], request.form['personalname'], request.form['additionalname'], 
         #                                    request.form['gender'], request.form['age'], request.form['year'], request.form['month'],
         #                                    request.form['day'], request.form['country'], request.form['city'], request.form['county'], 
         #                                    request.form['village'], request.form['other'], request.form['sos'], request.form['otherSOS'],
         #                                    request.form['password']])
          db.commit()
          session['personalname'] = request.form['personalname']   #added 3/13/17
          session['message'] = "Celebrate, " + session['personalname'] + ", you're alive! Hip, hip, hooray!"
          return redirect(url_for('celebrate'))                    #added 3/13/17
       else:
           error = "Not enough information to continue, please fill in asterisked/starred items."
           return render_template('signupSurvivor.html', error = error)
    else: #request.method == 'GET'
       return render_template('signupSurvivor.html', error = None)


@app.route('/loginSurvivor', methods = ['GET', 'POST'])
def loginSurvivor():
    """Handles survivor login to update information (loginSurvivor.html)."""  #WIP:more info needed
    render_template('loginSurvivor.html')    
    error = None
    return render_template('loginSurvivor.html', error = error)

 #NOTE: SQL syntax may go something like UPDATE survivors SET column1=value, column2=value WHERE some_column=some_value
 #always use the WHERE statement with an SQL UPDATE statement


#SEARCH VIEW FUNCTIONS
@app.route('/search', methods = ['POST', 'GET'])
def search():
    """Handles the search index screen (search.html)."""
    render_template('search.html', error = None)
    while request.method == 'POST':
        familyname = request.form['familyname']
        personalname = request.form['personalname']
        error = None
        message = ""
        if familyname and personalname: #for now to keep simple
           db = get_db()
           cur = db.execute("SELECT familyName, personalName FROM survivors WHERE familyName=familyname AND personalName=personalname")             
           msgDB = ""
           for row in cur.fetchall():
              if request.form['familyname'] in row and request.form['personalname'] in row:
                 msgDB = msgDB + str(row[1] + " " + row[0] + "... ")
              else:
                 msgDB = msgDB
           if msgDB == "":
              error = "No such survivor with that name has enrolled with I'mAlive."
              return render_template('search.html', error = error)
           else:
              session['personalname'] = request.form['personalname']
              session['familyname'] = request.form['familyname']
              session['message'] = "Celebrate! On [a certain date], " + session['personalname'] + " " + session['familyname'] + " registered with I'mAlive.  Hooray!" +  "WIP Message: these names pulled from the DB: " + msgDB
              return redirect(url_for('celebrate'))
        else:
            error = "Not enough information to continue; please provide both a family and a personal name. Thank you."
            return render_template('search.html', error = error)
    else: #request.method == 'GET'
        return render_template('search.html', error = None)
