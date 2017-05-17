I'mAlive
==========

I'mAlive is a prototype Python Flask CRUD web app for refugees and/or human trafficking victims to tell their families that they still live.

Motivation
----------
Many people lack access to more common social media platforms and/or, who due to safety issues, cannot share much identifying information about themselves online but want to let their families know that they live.  Such folks inspired the creation of I'mAlive.  I chose Flask, Python, and SQLite at the advice of professional programmers encouraging me to learn how to code and to use programming in pursuit of practically helping vulnerable people get out of harmful situations and into good ones.

Installation
------------
First install [Python 3][1], then [SQLite][2] and then [Flask][3], then do:

    > git clone https://github.com/esiram/imalive.git
    > cd imalive
    > export FLASK_APP=imalive
    > export FLASK_DEBUG=true
    > flask run

The 'imalive' app should now be running on `http://127.0.0.1:5000`.

Usage
-----

![home page](imalive/static/imalive-home.png)

![sign up](imalive/static/imalive-signup.png)

![celebrate sign up](imalive/static/imalive-celebrate-at-signup.png)

![update](imalive/static/imalive-update.png)

![search](imalive/static/imalive-search.png)

![celebrate at search](imalive/static/imalive-celebrate-at-search.png)


   [1]: https://www.python.org/
   [2]: https://sqlite.org/
   [3]: http://flask.pocoo.org/


 

