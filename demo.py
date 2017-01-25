import flask, flask.views, linecache, os, functools, json, ConfigParser, werkzeug, collections
from flask import g, request, render_template, jsonify
from flask_mysqldb import MySQL
from werkzeug import BaseRequest, responder
from werkzeug.wrappers import BaseRequest
from werkzeug.wsgi import responder
from werkzeug.exceptions import HTTPException, NotFound, Unauthorized, abort

app = flask.Flask(__name__)
print 'Flask name'
app.secret_key = "123"



########################################### DATABASE CONNETION ############################################


config = ConfigParser.SafeConfigParser()
config.read('/home/ziwg/config.ini')
app.config['MYSQL_MYSQL_USER'] = config.get('KEY', 'user')
app.config['MYSQL_PASSWORD'] = config.get('KEY', 'password')
app.config['MYSQL_DB'] = config.get('KEY', 'database')
app.config['MYSQL_HOST'] = config.get('KEY', 'host')
mysql = MySQL(app)
app.config['JSONIFY_PRETTYPRINT_REGULAR']


########################################### INTERFACE PART ################################################

@app.route('/applogin', methods=['POST'])
def applogin():
    appRequest = request.json
    checkIfUserIsInDatabase(str(appRequest['login']),str(appRequest['password']))
    return "Flask #1: Pomyslnie zalogowano do bazy"

@app.route('/appshowraces', methods=['POST'])
def appshowraces():
    listOfRaces = showRacesEntries()
    records = []        
    for race in listOfRaces:
        dictionary = collections.OrderedDict()
        dictionary['name'] = race[1]
        dictionary['userId'] = str(race[2])
        records.append(dictionary)
    result = json.dumps(records, indent=4)
    result = result.replace("[","{").replace("]","}")
    print result
    return result



########################################### INTERNAL MECHANISMS ###########################################

 
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
        mysqlCmd = ( "INSERT INTO `users`"
                     "(`user_username`,`user_password`,`user_privileges`)"
                     " VALUES ("
                     "'"+str(login)+"','"+str(password)+"','"+str(privileges)+"');"
                   ) 
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
        abort(401, "Flask #2: Niepoprawne dane uzytkownika")
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

def addInfoToRaceTable(name,userId,start,cp1,cp2,cp3,cp4,stop):
    print "Debug: wchodze do addInfoToRaceTable"    
    conn = mysql.connection
    cursor = conn.cursor()
    mysqlCmd = ("INSERT INTO `race` "
                "(`race_name`,`race_user_id`,`race_start`,`race_check_1`,`race_check_2`,`race_check_3`,`race_check_4`,`race_end`) "
                " VALUES (" + "'"
                +str(name)+"','"+str(userId)+"','"+str(start)+"','"+str(cp1)+"','"+str(cp2)+"','"+str(cp3)+"','"
                +str(cp4)+"','"+str(stop)+"')"
               )
    print mysqlCmd
    cursor.execute(mysqlCmd)
    return "Dodano informacje do tablicy wyscigow"

def removeRaceFromRaceTable(name):
    print "Debug: wejscie do removeRaceFromRaceTable"
    conn = mysql.connection
    cursor = conn.cursor()
    mysqlCmd = "DELETE FROM `race` WHERE race_name = "+"'"+str(name)+"'"
    print mysqlCmd
    cursor.execute(mysqlCmd)
    return "Wyscig zostal usuniety"

def showRacesEntries():
    print "Debug: wejscie do showRacesNames"
    conn = mysql.connection
    cursor = conn.cursor()
    listOfRaces = []
    cursor.execute("SELECT * FROM `race`")
    rows = cursor.fetchall()
    for row in rows:
        listOfRaces.append(row)
        print row
    print listOfRaces
    return listOfRaces

def showDesiredRaceEntries(name):
    print "Debug: wejscie do showDesiredRaceEntry"
    conn = mysql.connection
    cursor = conn.cursor()
    mysqlCmd = "SELECT * FROM `race` WHERE race_name = '"+str(name)+"'"
    listOfDesiredRaces = []
    cursor.execute(mysqlCmd)
    rows = cursor.fetchall()
    for row in rows:
        listOfDesiredRaces.append(row)
        print row
    print listOfDesiredRaces
    return listOfDesiredRaces


########################################### SITE METHODS AND LAYOUT  ######################################


class Main(flask.views.MethodView):
    def get(self):
        return flask.render_template('index.html')
    
    def post(self):
        if 'logout' in flask.request.form:
            flask.session.pop('username', None)
            return flask.redirect(flask.url_for('index'))
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


class ShowResults(flask.views.MethodView):
     @login_required
     def get(self):
         print "Debug: get wejscie"
         return flask.render_template('showResults.html')

     @login_required
     def post(self):        
        print "Debug: post wejscie 1"
        if 'showRaceRaces' in flask.request.form:
            listOfRaces = showRacesEntries()
           #flask.flash(str(usersList))
            racesNameList = []
            for race in listOfRaces:
                racesNameList.append(race[1])
            for raceName in racesNameList:
                print raceName
                flask.flash(raceName+u'\r\n')
        if 'raceNameToShowDesiredRace' in flask.request.form:
            raceNameRaces = flask.request.form['raceNameRaces']
            listOfDesiredRaces = showDesiredRaceEntries(raceNameRaces)
            for raceInfo in listOfDesiredRaces:
                print raceInfo
                flask.flash(str(raceInfo)+u'\r\n')
        return render_template('showResults.html')

class ManageRaces(flask.views.MethodView):
    def get(self):
        return flask.render_template('races.html')

    def post(self):
        print "Debug: post wejscie 2"
        if 'addRace' in flask.request.form:
            print "Debug: post add race wejscie"
            raceName = flask.request.form['raceName']
            userId = flask.request.form['userId']
            start = flask.request.form['start']
            cp1 = flask.request.form['cp1']
            cp2 = flask.request.form['cp2']
            cp3 = flask.request.form['cp3']
            cp4 = flask.request.form['cp4']
            stop = flask.request.form['stop']
            result = addInfoToRaceTable(raceName,userId,start,cp1,cp2,cp3,cp4,stop)
            flask.flash(result)
            print result
        if 'removeRace' in flask.request.form:
            print "Debug: post removeRace race wejscie"
            raceNameDelete = flask.request.form['raceNameDelete']
            result = removeRaceFromRaceTable(raceNameDelete)
            flask.flash(result)
        return flask.render_template('races.html')



app.add_url_rule('/',
                 view_func=Main.as_view('index'),
                 methods=["GET", "POST"])
app.add_url_rule('/add/',
                 view_func=Add.as_view('add'),
                 methods=['GET', 'POST',])
app.add_url_rule('/races/',
                 view_func=ManageRaces.as_view('races'),
                 methods=['GET', 'POST'])
app.add_url_rule('/results/',
                 view_func=ShowResults.as_view('results'),
                 methods=['GET', 'POST'])

app.debug = True
app.run('192.166.218.153')
