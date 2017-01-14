import flask, flask.views, linecache, os, functools, json, ConfigParser
from flask import g, request, render_template
from flask_mysqldb import MySQL

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


@app.route('/odpytaj')
def odpytaj():
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users LIMIT 1")    
    rows = cursor.fetchall()
    for row in rows:
        print row
    return str(rows)



DATABASE = 'flask.json'
users = {}
with open("uzytkownicy_org.txt") as f:
    for line in f:
        (key, val) = line.split()
        users[str(key)] = val

class Main(flask.views.MethodView):
    print 'class Main'
    def get(self):
        print 'get od maina'
        return flask.render_template('index.html')
    
    def post(self):
        print 'post od maina'
        if 'logout' in flask.request.form:
            flask.session.pop('username', None)
            return flask.redirect(flask.url_for('index'))
        required = ['username', 'passwd']
        for r in required:
            if r not in flask.request.form:
                flask.flash("Error: {0} is required.".format(r))
                return flask.redirect(flask.url_for('index'))
        username = flask.request.form['username']
        passwd = flask.request.form['passwd']
        if username in users and users[username] == passwd:
            flask.session['username'] = username
        else:
            flask.flash("Login lub haslo bledne!!!")
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
    print 'class Add'
    @login_required
    def get(self):
        print 'GET od Add'
        if 'userList' in flask.request.form:
            flask.flash('Niedlugo wyswietlanie listy uzytkownik bedzie dostepne')
        return flask.render_template('addUser.html')

    @login_required
    def post(self):
        print 'POST od Add'
        f = open('uzytkownicy_org.txt','ab')
        f.write(request.form['login']+' ')
        f.write(request.form['password']+'\n')
        f.close()
        fr = open('uzytkownicy_org.txt','rb').read()
        flask.flash("lista uzytkownikow:"+'\n')
        flask.flash(fr)
        return render_template('addUser.html')

class UserStats(flask.views.MethodView):
    @login_required
    def get(self):
        print 'GET od UserStats'
        return flask.render_template('show_entries.html')

    @login_required
    def post(self):
        print 'POST od UserStats'
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
        print 'GET od ShowResults'
        return flask.render_template('showResults.html')

    def post(self):
        print 'POST od ShowResults'
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
