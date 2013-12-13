import sqlite3, md5, string, random
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing

# configuration
DATABASE = '/tmp/shortener.db'
DEBUG = True
SECRET_KEY = 'development key'
HOST = 'http://localhost:5000/'

app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/mystories')
@app.route('/mystories/<sort>')
def myStories(sort=None):
		
	if session.get('logged_in'):
		user_id = session.get('user_id')
		name = str(g.db.execute('select username from users where id=?',[user_id]).fetchall())
		
		finalName = ''
		start = False
		end = False
		for x in name:
			
			if x == "'" and not end and start:
				end = True
				start = False
			if start:
				finalName += x
			if x == "'" and not start and not end:
				start = True
			
		name = finalName

		if sort=="short":
			flash("Sorted by short URL",'success')
			cur = g.db.execute('select short, long from urls where uid=? order by short asc',[user_id])
		elif sort=="long":
			flash("Sorted by long URL",'success')
			cur = g.db.execute('select short, long from urls where uid=? order by long asc',[user_id])
		else:
			cur = g.db.execute('select short, long from urls where uid=?',[user_id])

		urls = [dict(short=HOST+"server/short/"+row[0], long=row[1]) for row in cur.fetchall()]
		return render_template("mystories.html",name=name, urls=urls, pageName="mystories")
	flash("You are not logged in!",'info')
	return redirect(request.url_root)

@app.route('/server/short/<key>', methods=['GET'])
def getUrl(key):
	short = key
	if isinstance(short, unicode):
	    short = short.encode('utf-8')

	cur = g.db.execute('select long from urls where short=?',[short])
	existed_tuple = cur.fetchone()
	value = existed_tuple[0]
	if value is not None:
		return redirect(value) 
	else:
		flash("No result found",'info')
		return redirect(request.url_root)
		#return render_template('404.html'), 404

def isValid(url):
    return url[:4] == 'http'

@app.route('/server/shorts', methods=['POST'])
def addingUrl():
	if request.method == 'POST':
		key = request.form["short"]
		value = request.form["long"]

		if isinstance(key, unicode):
		    key = key.encode('utf-8')
		if isinstance(value, unicode):
			value = value.encode('utf-8')

		user_id = None
		
		if not isValid(value):
			value = 'http://' + value

        #db[str(key)]=value
		if session.get('logged_in'):
			user_id = session.get('user_id')

		g.db.execute('insert into urls (short, long, uid, custom) values (?, ?, ?, "true")',[key,value,user_id])
		g.db.commit()

		params = {'short':key,'long':value}

		return render_template('add_success.html',params=params, host=HOST+"server/short/")
	else:
		return render_template('badpage.html',params=params)

@app.route('/server/autoshort', methods=['POST'])
def auto_addingUrl():

	key = link_generator()
	value = request.form["long"]

	if not isValid(value):
		value = 'http://' + value

	if isinstance(key, unicode):
	    key = key.encode('utf-8')
	if isinstance(value, unicode):
		value = value.encode('utf-8')

	cur = g.db.execute('select short, long from urls where custom="false" and long=?',[value])
	existed_tuple = cur.fetchone()
	
	if existed_tuple != None:
		params = {'short':existed_tuple[0],'long':value}
		return render_template('add_success.html',params=params)

	cur = g.db.execute('select short from urls')
	all_shorts = cur.fetchall()

	# find a unique key
	while(key in all_shorts):
		key = link_generator()

	user_id = None
	if session.get('logged_in'):
		user_id = session.get('user_id')

	g.db.execute('insert into urls (short, long, uid, custom) values (?, ?, ?, "false")',[key,value,user_id])
	g.db.commit()
    
	params = {'short':key,'long':value}

	return render_template('add_success.html',params=params)

def link_generator(size=6, chars=string.ascii_lowercase + string.digits + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

@app.route('/create', methods=['GET'])
def showDevelopers():
    return render_template("create.html", pageName="create")

@app.route('/')
def home():
	return render_template('home.html',pageName="home")

########################## User Login, Logout, signup ##################################

@app.route('/login', methods=['GET','POST'])
def login():
	error = None
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		user = g.db.execute('select id, password from users where username = ?',
					[username]).fetchone()
		if user == None:
			flash('Invalid Username','danger')
		elif md5.new(password).hexdigest() != user[1]:
			flash('Invalid password','danger')
		else:
			session['logged_in'] = True
			session['user_id'] = user[0]
			flash('You are logged in','success')
			return redirect(url_for('mystories'))

	return redirect(request.url_root)

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	session.pop('user_id', None)
	flash('You are successfuly logged out', 'success')
	return redirect(request.url_root)

@app.route('/signup', methods=['GET','POST'])
def signup():
	error = None

	if request.method == 'POST':
		user_email = request.form['user_email']
		password = request.form['password']
		password2 = request.form['password2']
		
		if isinstance(user_email, unicode):
			user_email = user_email.encode('utf-8')
		
		if isinstance(password, unicode):
			password = password.encode('utf-8')
		
		if isinstance(password2, unicode):
			password2 = password2.encode('utf-8')

		if user_email != "" and password != "" and password2 == password:
			g.db.execute('insert into users (username, password) values (?, ?)',
					[user_email,md5.new(password).hexdigest()])
			g.db.commit()
			cur = g.db.execute('select id from users where username=?',[user_email])
			existed_tuple = cur.fetchone()
			session['logged_in'] = True
			session['user_id'] = existed_tuple[0]
			flash('User Created.','success')
		else:
			flash('please provide username and password.','warning')
			return redirect(url_for('signup'))
	return render_template('signup.html')

# DB setup related functions
def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		with app.open_resource('seed.sql', mode='r') as s:
			db.cursor().executescript(s.read())
		db.commit()

def connect_db():
	connection = sqlite3.connect(app.config['DATABASE'])
	#connection.text_factory = str
	return connection

@app.before_request
def before_request():
	g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
	db = getattr(g, 'db', None)
	if db is not None:
		db.close()
############################

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__== '__main__':
	app.run()