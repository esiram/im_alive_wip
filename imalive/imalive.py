### ALL IMPORTS ###
import os
import sqlite3
from datetime import datetime # per flask minitwit example 4/10/17
from hashlib import md5 # per flask minitwit example 4/10/17
from werkzeug import check_password_hash, generate_password_hash # this per flask minitwit example 4/10/17
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
    conn = connect_db()       #connection
    cur = conn.cursor()       #cursor (TBD: see init_db 'c' for cursor: determine if a general cursor object for the entire app should get made)
    cur.execute('CREATE TABLE IF NOT EXISTS survivors(familyname TEXT, personalname TEXT, signupdate TIMESTAMP)')#should I update the columns here????? the db has loaded regardless.-4/10/17
       

#FUNCTIONS TO INITIALIZE DB
def init_db():
    """Opens file from resource folder."""
    db = get_db()
    c = db.cursor()                #db.cursor() used in flaskr tutorial rather than c (TBD: does this duplicate the create_table 'cur' variable? Can you simplify?)
    with app.open_resource('schema.sql', mode='r') as f:
       c.executescript(f.read())
    db.commit()
    
@app.cli.command('initdb')  #flask creates an application context bound to correct application
def initdb_command():  #in the command line type: flask initdb
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
   if request.method == 'POST':  
       if 'doWhat' in request.form:    #should doWhat have a not null value????-ES 3/15/17
           doWhat = request.form['doWhat']
           if doWhat == "search":
              return redirect(url_for("search"))
           elif doWhat == "signup":
              return redirect(url_for("signupSurvivor"))
           else: # doWhat == "login":
              print("This should redirect to loginSurvivor.html.")
              return redirect(url_for("loginSurvivor"))
       else: #if nothing chosen but submit/enter button hit (i.e. doWhat = None); THIS DOESN'T WORK! Currently an error at redirections/rendering 'home.html'-es3/17/17
           return render_template('home.html', error = "Nothing selected: please click the circle next to the option you want, then click 'Submit.'  Thank you.")
   else:    #request.method == 'GET'
       return render_template('home.html', error = error)

#@app.route('/celebrate/<personalname>', methods = ['GET', 'POST']) #not pulling dynamic stuff into URL - Es 3/13/17
@app.route('/celebrate', methods = ['GET', 'POST'])
def celebrate():
    """Handles the celebrate screen (celebrate.html)."""
    if 'personalname' in session:                                                        #this pulls name dynamically into template, URL not showing yet as of 3/13/17
       return render_template('celebrate.html', personalname = session['personalname'], message = session['message'])  #this pulls name dynamically as of 3/13/17
    else:
       message= "Celebrate, you live!!!  If you want to look somoone else up, please check out the I'mAlive's Search page."
       return render_template('celebrate.html', message = message)

    
   
#SURVIVOR VIEW FUNCTIONS
@app.route('/signupSurvivor', methods = ['POST', 'GET'])
def signupSurvivor():
    """Handles survivor signup screen (signupSurvivor.html)."""
    render_template('signupSurvivor.html', error = None)
    if request.method == 'POST':
       error = None
       message = ""
       
       #form inputs:
       familyname = request.form['familyname']
       personalname = request.form['personalname']
       additionalname = request.form['additionalname']
       gender = None
       if 'gender' in request.form:
          gender = request.form['gender']
       age = request.form['age']
       year = request.form['year']
       month = request.form['month']
       day = request.form['day']
       country = request.form['country']
       state = request.form['state']
       city = request.form['city']
       county = request.form['county']
       village = request.form['village']
       other = request.form['other']
       sos = None
       if 'sos' in request.form:
          sos = request.form['sos']
       otherSOS = request.form['otherSOS']
       username = request.form['username']#### Will need to make this unique somehow, or just leave the password as a unique password???
       password = request.form['password']   #####  WORK ON HASHING and SALTING AT LATER DATE
       password2 = request.form['password2']
       ### if password2 == password:... else: error
       
       #automatic input:
       signupDate = 12122012  #hard code for now; later this should automatically update later
   
       if familyname and personalname and username and password == password2: #only requiring these
          db = get_db()
          db.execute('INSERT INTO survivors (familyName, personalName, additionalName, gender, age, year, month, day, country, state, city, county, village, other, sos, otherSOS, username, password, signupDate) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                      [familyname, personalname, additionalname, gender, age, year, month, day, country, state, city, county, village, other, sos, otherSOS, username, password, signupDate])
          db.commit()
          session['personalname'] = request.form['personalname']
          session['message'] = "Celebrate, " + session['personalname'] + ", you're alive! Hip, hip, hooray!"
          return redirect(url_for('celebrate'))
       elif password != password2:
          error = "The passwords do not match.  Please try again.  Thank you."
          return render_template('signupSurvivor.html', error = error)
       else:
           error = "Not enough information to continue, please fill in all asterisked/starred items."
           return render_template('signupSurvivor.html', error = error)
    else: #request.method == 'GET'
       return render_template('signupSurvivor.html', error = None)


@app.route('/loginSurvivor', methods = ['POST', 'GET'])
def loginSurvivor():
    """Handles survivor login to update information (loginSurvivor.html)."""  #WIP:more info needed
    render_template('loginSurvivor.html', error = None)
    if request.method == 'GET': #initially this is GET
       error = None
       return render_template('loginSurvivor.html', error = error)
    else: #request.method == 'POST':
       error = None
       personalname = request.form['personalname']
       familyname = request.form['familyname']
       username = request.form['username']  #SHOULD username BE UNIQUE IN schema.sql??? I think so.  Work on this.
       password = request.form['password']
       if personalname and familyname and username and password:
          db = get_db()   #this is redundant in different views, maybe make a function to call db and use the cursor later on???
          cur = db.execute("SELECT id, familyName, personalName, username, password FROM survivors WHERE familyName=familyname AND personalName=personalname AND username=username AND password=password")
          for row in cur.fetchall():
             if familyname == row[1] and personalname == row[2] and username == row[3] and password == row[4]:
                session['logged_in'] = True
                session['personalname'] = personalname
                session['username'] = username
                session['id'] = row[0]
                session['message'] = session['personalname'] + ", please verify the information about you in I'mAlive's database and update as needed.  Thank you."
                # flash("You are logged in.")
                return redirect(url_for('updateSurvivor'))
             else:
                error = "Try again please.  Something doesn't match."
                return render_template('loginSurvivor.html', error = error)
       else: #missing familyname, personalname, username and/or password
          error = "Please enter information in all fields.  Thank you."
          render_template('loginSurvivor.html', error = error)



@app.route('/updateSurvivor', methods = ['GET', 'POST'])
#@app.route('/updateSurvivor/<personalname>', methods = ['GET', 'POST'])
def updateSurvivor():
   """Handles survivor update information, only accessible when logged in."""
   render_template('updateSurvivor.html')
   error = None
   return render_template('updateSurvivor.html', error = error)

#NOTE: SQL syntax may go something like UPDATE survivors SET column1=value, column2=value WHERE some_column=some_value
#always use the WHERE statement with an SQL UPDATE statement
#I need to have an update info page so that pulls current info, but also shows all updates once updated.  Only folks a person logged in can access his/her personal page. """




#SEARCH VIEW FUNCTIONS
@app.route('/search', methods = ['POST', 'GET'])
def search():
    """Handles the search index screen (search.html)."""
    render_template('search.html', error = None)
    if request.method == 'POST':
        error = None
        message = ""
        
        #form inputs:
        familyname = request.form['familyname']
        personalname = request.form['personalname']
        additionalname = request.form['additionalname']
        gender = None
        if 'gender' in request.form:
           gender = request.form['gender']
        age = request.form['age']
        year = request.form['year']
        month = request.form['month']
        day = request.form['day']
        country = request.form['country']
        state= request.form['state']
        city = request.form['city']
        county = request.form['county']       
        village = request.form['village']
        other = request.form['other']

        if familyname or personalname: #when "or" used here instead of "and" it lists those with shared last names.-es 4/6/17 ### Q) should I only pull the not null values?-es 4/6/17
           db = get_db()
           cur = db.execute("SELECT id, familyName, personalName, additionalName, gender, age, year, month, day, country, state, city, county, village, other, signupDate FROM survivors WHERE familyName=familyname AND personalName=personalname AND additionalName=additionalname AND gender=gender AND age=age AND year=year AND month=month AND day=day AND country=country AND state=state AND city=city AND county=county AND village=village AND other=other")             
           msgDB = ""
           rowCount = 0
           idList = []
           lastDate = 0
           for row in cur.fetchall():   #when adding row[] later: note position change(s) from selected db columns
              if familyname in row[1] and personalname in row[2]:#This Works
                 msgDB = msgDB + str(row[2] + " " + row[1]) + " ID# " + str(row[0]) + "... "
                 rowCount = rowCount + 1
                 idList = idList + [row[0]]
                 lastDate = lastDate + row[15]
              else:
                 msgDB = msgDB
                 rowCount = rowCount
                 idList = idList
                 lastDate = lastDate
                 
           if msgDB == "":
              error = "No such survivor with that name has enrolled with I'mAlive."
              return render_template('search.html', error = error)
           
           elif rowCount != 1: # multiple survivors with similar info
              error = "I'mAlive has " + str(rowCount) + " people with this information registered in its database: " + msgDB + " Please provide more details."
              return render_template('search.html', error = error)
           
           else:#msgDB != "" and rowCount == 1
              session['personalname'] = request.form['personalname']
              session['familyname'] = request.form['familyname']
              session['lastDate'] = lastDate
              session['message'] = "Celebrate! On " + str(session['lastDate']) + " " + session['personalname'] + " " + session['familyname'] + " registered with I'mAlive.  Hooray!"
              return redirect(url_for('celebrate'))
        else:  
            error = "Not enough information to continue; please provide both a family name, a personal name, and a gender. Thank you."
            return render_template('search.html', error = error)
    else: #request.method == 'GET'
        return render_template('search.html', error = None)
