import flask, flask.views, linecache, os, functools, json, ConfigParser, werkzeug
from flask import g, request, render_template, jsonify
from flask_mysqldb import MySQL
from werkzeug import BaseRequest, responder
from werkzeug.wrappers import BaseRequest
from werkzeug.wsgi import responder
from werkzeug.exceptions import HTTPException, NotFound, Unauthorized, abort


app = flask.Flask(__name__)
print 'Flask name'
app.secret_key = "123"

config = ConfigParser.SafeConfigParser()
config.read('/home/ziwg/config.ini')
app.config['MYSQL_MYSQL_USER'] = config.get('KEY', 'user')
app.config['MYSQL_PASSWORD'] = config.get('KEY', 'password')
app.config['MYSQL_DB'] = config.get('KEY', 'database')
app.config['MYSQL_HOST'] = config.get('KEY', 'host')
mysql = MySQL(app)
app.config['JSONIFY_PRETTYPRINT_REGULAR']

@app.route('/test1', methods=['POST'])
def test1():
    content = request.json
    addUserToDatabase(str(content['login']),str(content['password']))
    return "Sru"

@app.route('/test2', methods=['POST'])
def test2():
    content = request.json
    removeUserToDatabase(str(content['login']))
    return "Sru"


@app.route('/test3', methods=['POST'])
def test3():
    content = request.json
    checkIfUserIsInDatabase(str(content['login']),str(content['password']))
    return "Sru"

@app.route('/test4', methods=['POST'])
def test4():
    showUsersInDatabase()
    return "Sru"


def addUserToDatabase(login,password):
    print 'addUserToData'
    conn = mysql.connection
    cursor = conn.cursor()
    ifLoginExists = 0
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    for row in rows:
        if login == row[1] and password == row[2]:
            ifLoginExists = 1
    if ifLoginExists == 1:
        print "Debug: Nie dodano uzytkownika poniewaz jest juz w bazie"
        return "Nie dodano uzytkownika poniewaz jest juz w bazie"
    else:
        privileges = 0
        mysqlCmd = "INSERT INTO `users` (`user_username`,`user_password`,`user_privileges`) VALUES ("+"'"+str(login)+"','"+str(password)+"','"+str(privileges)+"');"
        print mysqlCmd
        cursor.execute(mysqlCmd)
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        for row in rows:
            print row
        return "Dodano uzytkownika do bazy danych"

def removeUserFromDatabase(login):
    conn = mysql.connection
    cursor = conn.cursor()
    ifLoginExists = 0
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    for row in rows:
        if login == row[1]:
            ifLoginExists = 1
    if ifLoginExists == 0:
        return "Nie usunieto  uzytkownika poniewaz nie ma go w bazie"
    else:
       mysqlCmd = "DELETE FROM `users` WHERE user_username = "+"'"+str(login)+"'"
       cursor.execute(mysqlCmd)
       cursor.execute("SELECT * FROM users")
       rows = cursor.fetchall()
       for row in rows:
           print row
       return "Uzytkownik o podanym loginie zostal usuniety z bazy"

def checkIfUserIsInDatabase(login,password):
    conn = mysql.connection
    cursor = conn.cursor()
    mysqlCmd = "SELECT * FROM users"
    ifLoginCorrect = False
    cursor.execute(mysqlCmd)
    rows = cursor.fetchall()
    for row in rows:
        if login == row[1] and password == row[2]:
            ifLoginCorrect = True
    if ifLoginCorrect == True:
        print "Debug: uzytkownik jest"
        return True
    else:
        print "Debug: uzytkownika nie ma"
        abort(401)
        return False

def listRaceTableFromDatabase():
    return True

def showUsersInDatabase():
    conn = mysql.connection
    cursor = conn.cursor()
    listOfUsers = []
    cursor.execute("SELECT * FROM `users`")
    rows = cursor.fetchall()
    for row in rows:
        listOfUsers.append(row)
        print row
    print listOfUsers
    return listOfUsers


@app.route('/addlogin', methods=['POST'])
def addlogin():
    content = request.json
    conn = mysql.connection
    cursor = conn.cursor()
    msg = "INSERT INTO `users` (`user_username`,`user_password`) VALUES ("+"'"+str(content['login'])+"','"+str(content['password'])+"'"+")"
    print msg
    cursor.execute(msg)
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    for row in rows:
        print row
    login = {content['login']:content['password']}
    return json.dumps(login, indent=4)

@app.route('/json', methods=['POST'])
def jsonTesting():
    content = request.json
    conn = mysql.connection
    cursor = conn.cursor()
    login = content['login'] 
    password = content['password']
    ifLoginCorrect = 0
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    for row in rows:
        if login == row[1] and password == row[2]:
            ifLoginCorrect = 1
    if ifLoginCorrect == 1:
        return str(ifLoginCorrect)
    else:
        abort(401)
        return str(ifLoginCorrect)




class Main(flask.views.MethodView):
    def get(self):
        return flask.render_template('index.html')
    
    def post(self):
        if 'logout' in flask.request.form:
            flask.session.pop('username', None)
            return flask.redirect(flask.url_for('index'))
        # required = ['username', 'password']
        # for r in required:
        #     if r not in flask.request.form:
        #         flask.flash("Error: {0} is required.".format(r))
        #         return flask.redirect(flask.url_for('index'))
        username = flask.request.form['username']
        password = flask.request.form['password']
        ifLoginProperly = 0
        content = request.json
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        for row in rows:
            print row
            if username == row[1] and password == row[2]:
                flask.session['username'] = username
                ifLoginProperly = 1
        if ifLoginProperly == 0:
            flask.flash("Login lub haslo bledne")
        if 'gosc' in flask.request.form:
            print 'Proba logowania jako gosc'

        return flask.redirect(flask.url_for('index'))

def login_required(method):
    print 'login required'
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        if 'username' in flask.session:
            return method(*args, **kwargs)
        else:
            flask.flash("Wymagane logowanie")
            return flask.redirect(flask.url_for('index'))
    return wrapper

class Add(flask.views.MethodView):
    @login_required
    def get(self):
        return flask.render_template('addUser.html')

    @login_required
    def post(self):
        if 'userList' in flask.request.form:
            listOfUsers = showUsersInDatabase()
            #flask.flash(str(usersList))
            loginList = []
            for user in listOfUsers:
                loginList.append(user[1])
            for logins in loginList:
		print logins 
                flask.flash(logins+u'\r\n')
            #flask.flash('Niedlugo wyswietlanie listy uzytkownik bedzie dostepne')
        content = request.json
        conn = mysql.connection
        cursor = conn.cursor()
	if 'addUser' in flask.request.form:
            username = flask.request.form['login']
            password = flask.request.form['password']
            result = addUserToDatabase(username,password)
            flask.flash(result)
            print 'po wyjsciu z funkcji dodawania'
            cursor.execute("SELECT * FROM users")
	    rows = cursor.fetchall()
	    for row in rows:
	        print row
	if 'removeUser' in flask.request.form:
	    userToRemoved = flask.request.form['login_to_removed'] 
	    print userToRemoved
	    result = removeUserFromDatabase(userToRemoved)
            flask.flash(result)
        return render_template('addUser.html')

#DATABASE="flask.json"

class ShowRaces(flask.views.MethodView):
     @login_required
     def get(self):
         return flask.render_template('races.html')

     @login_required
     def post(self):
         return render_template('races.html')

#class UserStats(flask.views.MethodView):
#    @login_required
#    def get(self):
#        return flask.render_template('show_entries.html')

#    @login_required
#    def post(self):
#        try:
#            db = open(DATABASE).read()
#        except IOError:
#            db = '{"entries":[]}'
#        g.db = json.loads(db)
#        g.db['entries'].insert(0, {
#        'title': request.form['title'],
#        'text':request.form['text']
#        })
#        if hasattr(g,'db'):
#            open(DATABASE, 'w').write(json.dumps(g.db, indent=4))
#        return render_template('show_entries.html', entries=g.db['entries'])

class ShowResults(flask.views.MethodView):
    def get(self):
        return flask.render_template('showResults.html')

    def post(self):
        if 'showResult' in flask.request.form:
            try:
                db = open(DATABASE).read()
            except IOError:
                db = '{"entries":[]}'
            g.db = json.loads(db)
            return flask.render_template('showResults.html', entries=g.db['entries'])
        return flask.render_template('showResults.html')

app.add_url_rule('/',
                 view_func=Main.as_view('index'),
                 methods=["GET", "POST"])
app.add_url_rule('/add/',
                 view_func=Add.as_view('add'),
                 methods=['GET', 'POST',])
app.add_url_rule('/races/',
                 view_func=ShowRaces.as_view('races'),
                 methods=['GET', 'POST'])
app.add_url_rule('/results/',
                 view_func=ShowResults.as_view('results'),
                 methods=['GET', 'POST'])

app.debug = True
app.run('192.166.218.153')
