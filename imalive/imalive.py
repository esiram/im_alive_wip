"""As time permits, work on: 1) Backend:
                                 a)upper and lower cases in search view (note: you may use html functionality for this; research to see which is better)
                                 b) change password section needs to get added
                             2) Frontend:
                                 a) modify/beautify frontend views """

"""I'mAlive's primary goal: to give families of refugees and families of human trafficking victims hope and peace through the knowledge that their loved ones still live.  I'mAlive focuses on those lacking access to more common social media platforms and/or those, who because of safety issues, cannot risk sharing much identifying information but who want their families to know that they live."""

### ALL IMPORTS ###
import os
import sqlite3
import time
import datetime
import random
from hashlib import md5 
from werkzeug import check_password_hash, generate_password_hash
from flask import Flask, request, session, g, redirect, url_for, abort, render_template


### CONFIGURATION CODE ###
"""This loads the default configuration and over-rides the environment variable configuration."""

app = Flask(__name__)                #creates & initiates app instance
app.config.from_object(__name__)     #loads config from this file

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'imalive.db'),
    SECRET_KEY='development key',      #for sessions
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
    """Creates table 'survivors' if table doesn't exist."""
    conn = connect_db()       
    cur = conn.cursor()       #cursor (TBD: see init_db 'c' for cursor: determine if a general cursor object for the entire app should get made)
    cur.execute('CREATE TABLE IF NOT EXISTS survivors(familyName TEXT, personalName TEXT, additionalName TEXT, gender TEXT, age INTEGER, year INTEGER, month INTEGER, day INTEGER, country TEXT, state TEXT, city TEXT, county TEXT, village TEXT, other TEXT, sos TEXT, otherSOS TEXT, username TEXT, password TEXT, signupDate TIMESTAMP, updateDate TIMESTAMP)')
       

#FUNCTIONS TO INITIALIZE DB
def init_db():
    """Opens file from resource folder."""
    db = get_db()
    c = db.cursor()
    with app.open_resource('schema.sql', mode='r') as f:
       c.executescript(f.read())
    db.commit()
    
@app.cli.command('initdb')  #flask creates application context bound to correct application
def initdb_command():  #to reset DB: in the command line type *flask initdb*
    """Initializes the database."""
    init_db()
    print('Initialized the database.')


    
### VIEW FUNCTIONS ###

#GENERAL VIEW FUNCTIONS
@app.route('/', methods = ['POST', 'GET'])
@app.route('/home', methods = ['POST', 'GET'])
def home():
   """ Handles home screen. """
   session['logged_in'] = False    #to verify session is logged out
   print(session['logged_in'])     #developer help: should print *False* if logged out
   message = "Welcome to I'mAlive!"
   #if 'message' in session:
   #   message= session['message']
   error = None
   if 'error' in session:
     error = session['error']
   render_template('home.html', error = error, message = message)
   if request.method == 'POST':  
       if 'doWhat' in request.form:
           doWhat = request.form['doWhat']
           if doWhat == "search":
              return redirect(url_for("search"))
           elif doWhat == "signup":
              return redirect(url_for("signupSurvivor"))
           else:                    #doWhat == "login"
              return redirect(url_for("loginSurvivor"))
       else:                        #if nothing chosen but submit/enter button clicked
           error  = "Nothing selected: please click the circle next to the option you want, then click 'Submit.'  Thank you."
           return render_template('home.html', error = session['error'], message = message)
   else:                            #request.method == 'GET'
      return render_template('home.html', error = error, message = message)


@app.route('/celebrate', methods = ['GET', 'POST'])    
@app.route('/celebrate/<personalname>', methods = ['GET', 'POST'])
def celebrate(personalname = None):
    """Handles the celebrate screen."""
    personalname = None
    error = None
    message = None
    if 'message' in session:
       message = session['message']
    if 'personalname' in session:              
       return render_template('celebrate.html', personalname = personalname, message = message, parent = "..")
    else:                           #personalname not in session
       message= "Rejoice, you live!!!  If you want to look someone else up, please check out the I'mAlive Search page."
       return render_template('celebrate.html', message = message, parent = "", personalname = "")

    

#SURVIVOR VIEW FUNCTIONS
@app.route('/signupSurvivor', methods = ['POST', 'GET'])
def signupSurvivor():
   """Handles survivor signup screen."""
   render_template('signupSurvivor.html', error = None)
   if request.method == 'GET':
      return render_template('signupSurvivor.html', error = None)
   else:                 # request.method == 'POST':
      error = None
      message = ""
      familyname = request.form['familyname']
      personalname = request.form['personalname']
      additionalname = request.form['additionalname']
      gender = "" 
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
      sos = ""
      if 'sos' in request.form:
         sos = request.form['sos']
      otherSOS = request.form['otherSOS']
      username = request.form['username']
      if len(username) < 5 or len(username) > 20:
         error = "Username must have between 5 and 20 characters."
         return render_template('signupSurvivor.html', error = error)
      else: #username >= 5 and username <= 20 characters
         db = get_db()
         cur = db.execute("SELECT * FROM survivors WHERE username=?", [username])
         dbresult = cur.fetchall()
         if len(dbresult) != 0:
            error = "Username already taken, please provide a different username."
            return render_template('signupSurvivor.html', error = error)
      password = request.form['password']
      if len(password) < 5 or len(password) > 20:
         error = "Password must have between 5 and 20 characters."
         return render_template('signupSurvivor.html', error = error)
      elif password.isalnum() != True:
         error = "Passwords can only have alphabetic and/or numeric characters."
         return render_template('signupSurvivor.html', error = error)
      password2 = request.form['password2']      
      signupDate = str(datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S')) #see example on pythonprogramming.net
      if familyname and personalname and username and password == password2:
         db = get_db()
         db.execute('INSERT INTO survivors (familyName, personalName, additionalName, gender, age, year, month, day, country, state, city, county, village, other, sos, otherSOS, username, password, signupDate) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                    [familyname, personalname, additionalname, gender, age, year, month, day, country, state, city, county, village, other, sos, otherSOS, username, generate_password_hash(password), signupDate])
         db.commit()
         session['personalname'] = request.form['personalname']
         session['message'] = "Celebrate, " + session['personalname'] + ", you're alive! Hip, hip, hooray!"
         return redirect(url_for('celebrate', personalname = session['personalname']))
      elif password != password2:
         error = "The passwords do not match.  Please try again.  Thank you."
         return render_template('signupSurvivor.html', error = error)
      else:
         error = "Not enough information to continue, please fill in all asterisked/starred items."
         return render_template('signupSurvivor.html', error = error)


@app.route('/loginSurvivor', methods = ['GET', 'POST'])
def loginSurvivor(error=None):
    """Handles survivor login to update information."""
    if request.method == 'GET':
       error = None
       if 'error' in session:
          error = session['error']
       session['logged_in'] = False
       return render_template('loginSurvivor.html')
    else:                 #request.method == 'POST':
       username = request.form['username']
       password = request.form['password']
       if username and password:
          db = get_db()
          cur = db.execute('SELECT * FROM survivors WHERE username = ?', [username])
          dbresult = cur.fetchall()
          if len(dbresult) != 1:
             error = "Invalid username."
          else:           #only one result pulls from db 
             result = dbresult[0]
             if check_password_hash(result[18], password) != True:
                error = "Invalid password."
             else:        #password hash returns True
                session['logged_in'] = True
                session['userID'] = result[0]
                session['personalname'] = result[2]
                session['username'] = result[17]
                session['message'] = session['personalname'] + ", please verify your information in I'mAlive's database and update as needed."
                print("Logged in session ID = " + str(session['userID']) + " for name " + session['personalname'] + ".") #developer aid
                return redirect(url_for("updateSurvivor", personalname=session['personalname']))
       else:              #missing username/password
             error = "Please provide both a valid username and the associated password."
       return render_template('loginSurvivor.html', error=error)

    
@app.route('/logout')
def logout():
   """Handles logging user out."""
   session.pop('logged_in', None)
   session['logged_in'] = False
   print("Logged_in Status: " + str(session['logged_in'] == True)) #developer aid
   session['error'] = "Current status: logged out."
   return redirect(url_for('home', error=session['error']))


@app.route('/updateSurvivor', methods = ['GET', 'POST'])
@app.route('/updateSurvivor/<personalname>', methods = ['GET', 'POST'])
def updateSurvivor(personalname=None):
   """Handles survivor update information, only accessible when logged in."""
   if request.method == 'GET':
      if session['logged_in'] != True:
         session['error'] = "LoggedOut"
         return redirect(url_for("loginSurvivor", error=session['error']))
      else:                #session['logged_in'] == True
         print("session['logged_in'] == True: ", session['logged_in'] == True)
         error = None
         if 'error' in session:
            error = session['error']
         username = ""
         if 'username' in session:
            username = session['username']
         message = ""
         if 'message' in session:
            message = session['message']
         personalname = ""
         if 'personalname' in session:
            personalname = session['personalname']
         familyname2 = ""
         personalname2 = ""
         additionalname2 = ""
         gender2 = ""
         age2 = ""
         year2 = ""
         month2 = ""
         day2 = ""
         country2 = ""
         state2 = ""
         city2 = ""
         county2 = ""
         village2 = ""
         other2 = ""
         sos2 = ""
         otherSOS2 = ""
         signupDate = ""
         userID = None
         if 'userID' in session:
            userID = session['userID']
         db = get_db()
         cur = db.execute('SELECT * FROM survivors WHERE username=? AND id=?', [username, userID])
         dbresult = cur.fetchall()
         if len(dbresult) == 0 or len(dbresult) > 1:
            error = "Could not find survivor in database."
         else:                     #if len(dbresult) == 1  (i.e. only one record pulled from survivors table)
            result = dbresult[0]
            print("id: " + str(result[0]) + " personalname: " + result[2])
            familyname2 = str(result[1])
            personalname2 = str(result[2])
            additionalname2 = str(result[3])
            gender2 = str(result[4])
            age2 = str(result[5])
            year2 = str(result[6])
            month2 = str(result[7])
            day2 = str(result[8])
            country2 = str(result[9])
            state2 = str(result[10])
            city2 = str(result[11])
            county2 = str(result[12])
            village2 = str(result[13])
            other2 = str(result[14])
            sos2 = str(result[15])
            otherSOS2 = str(result[16])
            signupDate = str(result[17])
      return render_template('updateSurvivor.html', message = session['message'], personalname = session['personalname'], familyname2 = familyname2, personalname2 = personalname2, additionalname2 = additionalname2, gender2 = gender2, age2 = age2, year2 = year2, month2 = month2, day2 = day2, country2 = country2, state2 = state2, city2 = city2, county2 = county2, village2 = village2, other2 = other2, sos2 = sos2, otherSOS2 = otherSOS2, signupDate = signupDate)
   else:                           #request.method == 'POST'
      if session['logged_in'] != True:
         error = "Logged out."
         #session['error'] = "LoggedOut"
         return redirect(url_for("loginSurvivor", error=error))
      else:                        #session['logged_in'] == True
         error = "POST VIEW ERROR MESSAGE"
         username = session['username']
         if not username:
            error = "Username not found in ImAlive's database."
         print("Username: " + str(username))  #developer help
         if 'delete' in request.form:
            delete = request.form['delete']
            if delete == "Yes":
               return redirect(url_for("deleteSurvivor", personalname=session['personalname']))
         else:
            db = get_db()
            cur = db.execute('SELECT * FROM survivors WHERE username=? AND id=?', [username, session['userID']])
            dbresult = cur.fetchall()
            if len(dbresult) == 0 or len(dbresult) > 1:
               error = "Not found in I'mAlive's database."
            else:                    #only one row pulls from db
               result = dbresult[0]
               additionalname = str(result[3])
               if 'additionalname' in request.form and request.form['additionalname'] != "":
                  additionalname = request.form['additionalname']
               gender = str(result[4])   
               if 'gender' in request.form and request.form['gender'] != "":
                  gender = request.form['gender']
               age = str(result[5])
               if 'age' in request.form and request.form['age'] != "":
                  age = request.form['age']
               year = str(result[6])
               if 'year' in request.form and request.form['year'] != "":
                  year = request.form['year']
               month = str(result[7])
               if 'month' in request.form and request.form['month'] != "":
                  month = request.form['month']
               day = str(result[8])
               if 'day' in request.form and request.form['day'] != "":
                  day = request.form['day']
               country = str(result[9])
               if 'country' in request.form and request.form['country'] != "":
                  country = request.form['country']
               state = str(result[10])
               if 'state' in request.form and request.form['state'] != "":
                  state = request.form['state']
               city = str(result[11])
               if 'city' in request.form and request.form['city'] != "":
                  city = request.form['city']
               county = str(result[12])
               if 'county' in request.form and request.form['county'] != "":
                  county = request.form['county']
               village = str(result[13])
               if 'village' in request.form and request.form['village'] != "":
                  village = request.form['village']
               other = str(result[14])
               if 'other' in request.form and request.form['other'] != "":
                  other = request.form['other']
               sos = str(result[15])
               if 'sos' in request.form and request.form['sos'] != "":
                  sos = request.form['sos']
               otherSOS = str(result[16])
               if 'otherSOS' in request.form and request.form['otherSOS']!= "":
                  otherSOS = request.form['otherSOS']
              # if 'password' in session:   
              #    password = session['password']   
              # if 'password' in request.form and request.form['password'] == "Yes":  #THIS NEEDS WORK
              #    error = "Cannot change password at this time."
              #    session['message'] = error
              #    return redirect(url_for("home"))
               updateDate = str(datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S'))
               db.execute("UPDATE survivors SET additionalName=?, gender=?, age=?, year=?, month=?, day=?, country=?, state=?, city=?, county=?, village=?, other=?, sos=?, otherSOS=?, updateDate=? WHERE username=?", [additionalname, gender, age, year, month, day, country, state, city, county, village, other, sos, otherSOS, updateDate, username])
               db.commit()
            return redirect(url_for("updateSurvivor", personalname=session['personalname'])) 
            

@app.route('/deleteSurvivor', methods = ['GET', 'POST'])  
@app.route('/deleteSurvivor/<personalname>', methods = ['GET', 'POST'])
def deleteSurvivor(personalname=None):
   """Handles deleting a survivor's file."""
   if request.method == 'GET':
      error = "Please confirm that you wish to delete this account.  Thank you."
      return render_template('deleteSurvivor.html', error = error)
   else:                          #request.method == 'POST'
      error = None
      delete = ""
      if 'delete' in request.form and request.form['delete']:
         delete = request.form['delete']
      username = ""
      if 'username' in request.form:
         username = request.form['username']
      password = ""
      if 'password' in request.form:
         password = request.form['password']
      if delete == "yes":
         if username == "":
            error = "Username required."
            return render_template('deleteSurvivor.html', error = error)
         elif password == "":
            error = "Password required."
            return render_template('deleteSurvivor.html', error = error)
         else:                 #username and password in request.form
            db = get_db()
            cur = db.execute("SELECT * FROM survivors WHERE username=?", [username])
            dbresult = cur.fetchall()
            if len(dbresult) != 1:
               error = "Invalid username."
               return render_template('deleteSurvivor.html', error = error)
            else:              #len(dbresult) == 1
               result = dbresult[0]
               if check_password_hash(result[18], password) != True:
                  error = "Invalid password."
               else:           #only one result pulls from db and password hash returns True
                  print("id = " + str(result[0]))  #developer check
                  session['username'] = request.form['username']
                  db.execute("DELETE FROM survivors WHERE username=?", [username])
                  db.commit()
                  print("Deleted row in db for username" + str(username)) #developer check
                  session['message'] = "Account deleted for: " + session['username'] 
                  return redirect(url_for("home"))
            return render_template('deleteSurvivor.html', error = error)
      elif delete == "no":
         return redirect(url_for("home"))      
      else:                   #delete = ""
         error = "Nothing chosen; please submit your selection: yes or no."
         return render_template('deleteSurvivor.html', error = error)
         


#SEARCH VIEW FUNCTIONS
@app.route('/search', methods = ['POST', 'GET'])
def search():
    """Handles the search index screen (search.html)."""
    render_template('search.html', error = None)
    if request.method == 'POST':
        error = None
        message = ""
        familyname = request.form['familyname']
        personalname = request.form['personalname']
        select = "SELECT * FROM survivors WHERE familyName=? AND personalName=?"
        select2 = [familyname, personalname]
        additionalname = ""
        if 'additionalname' in request.form and request.form['additionalname'] != "":
           additionalname = request.form['additionalname']
           select = select + " AND additionalName=?"
           select2 = select2 + [additionalname]
        if 'gender' in request.form and request.form['gender'] != None: 
           gender = request.form['gender']
           select = select + " AND gender=?"
           select2 = select2 + [gender]
        age = ""
        if 'age' in request.form and request.form['age'] != "":
           age = request.form['age']
           select = select + " AND age=?"
           select2 = select2 + [age]
        year = ""
        if 'year' in request.form and request.form['year'] != "":
           year = request.form['year']
           select = select + " AND year=?"
           select2 = select2 + [year]
        month = ""
        if 'month' in request.form and request.form['month'] != "":
           month = request.form['month']
           select = select + " AND month=?"
           select2 = select2 + [month]
        day = ""
        if 'day' in request.form and request.form['day'] != "":
           day = request.form['day']
           select = select + " AND day=?"
           select2 = select2 + [day]
        country = ""
        if 'country' in request.form and request.form['country'] != "":
           country = request.form['country']
           select = select + " AND country=?"
           select2 = select2 + [country]
        state = ""
        if 'state' in request.form and request.form['state'] != "":
           state = request.form['state']
           select = select + " AND state=?"
           select2 = select2 + [state]
        city = ""
        if 'city' in request.form and request.form['city'] != "":
           city = request.form['city']
           select = select + " AND city=?"
           select2 = select2 + [city]
        county = ""
        if 'county' in request.form and request.form['county'] != "":
           county = request.form['county']
           select = select + " AND county=?"
           select2 = select2 + [county]
        village = ""
        if 'village' in request.form and request.form['village'] != "":
           village = request.form['village']
           select = select + " AND village=?"
           select2 = select2 + [village]
        other = ""
        if 'other' in request.form and request.form['other'] != "":   
           other = request.form['other']
           select = select + " AND other=?"
           select2 = select2 + [other]
        if familyname and  personalname: 
           db = get_db()
           cur = db.execute(select, select2)
           print(select, select2)
           dbresult = cur.fetchall()
           if len(dbresult) == 0:          #no survivor pulls from db
              error = "I'mAlive does not show anyone with that name actively enrolled in its database."
              return render_template('search.html', error = error)
           elif len(dbresult) > 1:         #multiple survivors pulled from db with similar information
              msgDB = ""
              for row in dbresult: 
                 msgDB = msgDB + str(row[2] + " " + row[1]) + " ID# " + str(row[0]) + "... "
                 error = "I'mAlive has " + str(len(dbresult)) + " people with this information registered in its database: " + msgDB + " Please provide more details."
              return render_template('search.html', error = error)
           else:                           #one survivor pulls from db (i.e. len(dbresult) == 1)
              result = dbresult[0]
              session['personalname'] = request.form['personalname']
              session['familyname'] = request.form['familyname']
              lastDate = result[19]
              session['lastDate'] = lastDate
              if result[20] and result[20] != None:
                 lastDate = result[20]
                 session['lastDate'] = lastDate
                 session['message'] = "Celebrate! " + session['personalname'] + " " + session['familyname'] + " updated his/her I'mAlive account on " + str(session['lastDate']) + ".  Hooray!!!"
              session['message'] = "Celebrate! On " + str(session['lastDate']) + " " + session['personalname'] + " " + session['familyname'] + " registered with I'mAlive.  Hooray!"
              return redirect(url_for('celebrate', personalname = session['personalname']))
        else:                               #missing familyname and/or personalname
            error = "Not enough information to continue; please provide both a family name and a personal name. Thank you."
            return render_template('search.html', error = error)
    else:                                   #request.method == 'GET'
        return render_template('search.html', error = None)
