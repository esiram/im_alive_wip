import sqlite3
import datetime #for datestamp
import time #for populating unix (may not be necessary// delete later if not used)

#FUNCTIONS TO CONNECT DB
def connect_db():
   """Connects to specific database."""
   rv = sqlite3.connect(app.config['DATABASE'])  #in another tutorial "rv" was named "conn"
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
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv
       

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
