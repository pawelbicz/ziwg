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


@app.route('/odpytaj')
def odpytaj():
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users LIMIT 1")    
    rows = cursor.fetchall()
    for row in rows:
        print row
    return str(rows)


@app.route('/addlogin', methods=['POST'])
def addlogin():
    content = request.json
    conn = mysql.connection
    cursor = conn.cursor()
#    msg = 'SELECT * FROM users LIMIT 1'
    msg = "INSERT INTO `users` (`user_username`,`user_password`) VALUES ("+"'"+str(content['login'])+"','"+str(content['passw'])+"'"+")"
    print msg
#    msg = "INSERT INTO `users` (`user_username`,`user_password`) VALUES ('leszek','haslo')"
#    print msg
    cursor.execute(msg)
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    for row in rows:
        print row
    login = {content['login']:content['passw']}
    return json.dumps(login, indent=4)

@app.route('/json', methods=['POST'])
def jsonTesting():
    content = request.json
    conn = mysql.connection
    cursor = conn.cursor()
    login = content['login'] 
    passw = content['passw']
    ifLoginCorrect = 0
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    for row in rows:
        if login == row[1] and passw == row[2]:
            ifLoginCorrect = 1
    if ifLoginCorrect == 1:
        return str(ifLoginCorrect)
    else:
        abort(401)
        return str(ifLoginCorrect)


    #obj = [[1,2,3],(1,2,3),123,123.123,'abc',{'key1':(1,2,3),'key2':(4,5,6)}]
    # Convert python object to json
    #obj2 = {'login':'fikcyjny','passw':'fikcyjne'},{'login':'fikcyjny','passw':'fikcyjne'}

    #json_string = json.dumps(obj)
    #print 'Json: %s' % json_string
    #abort(401)
    #return json.dumps(obj2, indent=4)
    #if request.method == "POST":
#       zmienna = request.form['login']
    #    content = request.json
    #    print content['login']
    #    return jsonify(login=content['login'],passw=content['passw'])
#        return jsonify(login=request.form['login'],passw=request.form['passw'])  
#    return 'blad'


DATABASE = 'flask.json'

class Main(flask.views.MethodView):
    def get(self):
        return flask.render_template('index.html')
    
    def post(self):
        if 'logout' in flask.request.form:
            flask.session.pop('username', None)
            return flask.redirect(flask.url_for('index'))
        # required = ['username', 'passwd']
        # for r in required:
        #     if r not in flask.request.form:
        #         flask.flash("Error: {0} is required.".format(r))
        #         return flask.redirect(flask.url_for('index'))
        username = flask.request.form['username']
        passwd = flask.request.form['passwd']
        ifLoginProperly = 0
        content = request.json
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        for row in rows:
            print row
            if username == row[1] and passwd == row[2]:
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
            flask.flash('Niedlugo wyswietlanie listy uzytkownik bedzie dostepne')
        content = request.json
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        username = flask.request.form['login']
        passwd = flask.request.form['password']
        print username, passwd
        mysqlCmdAddUser = "INSERT INTO `users` (`user_username`,`user_password`) VALUES ("+"'"+username+"','"+passwd+"'"+")"
        print mysqlCmdAddUser
        cursor.execute(mysqlCmdAddUser)
        rows = cursor.fetchall()
        for row in rows:
            print row
        #    msg = "INSERT INTO `users` (`user_username`,`user_password`) VALUES ('leszek','haslo')"
        # flask.flash("lista uzytkownikow:"+'\n')
        # flask.flash(fr)
        return render_template('addUser.html')

class UserStats(flask.views.MethodView):
    @login_required
    def get(self):
        return flask.render_template('show_entries.html')

    @login_required
    def post(self):
        try:
            db = open(DATABASE).read()
        except IOError:
            db = '{"entries":[]}'
        g.db = json.loads(db)
        g.db['entries'].insert(0, {
        'title': request.form['title'],
        'text':request.form['text']
        })
        if hasattr(g,'db'):
            open(DATABASE, 'w').write(json.dumps(g.db, indent=4))
        return render_template('show_entries.html', entries=g.db['entries'])

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
app.add_url_rule('/stats/',
                 view_func=UserStats.as_view('stats'),
                 methods=['GET', 'POST'])
app.add_url_rule('/results/',
                 view_func=ShowResults.as_view('results'),
                 methods=['GET', 'POST'])

app.debug = True
app.run('192.166.218.153')
