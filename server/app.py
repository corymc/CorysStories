# Note: this file is no longer used in our application. 
# This was used for part I and our start of part II, but we decided to switch to a relational database.
# Our current application file is shortener.py.
# Instructions on running our application can be found in the README file.

import shelve
from subprocess import check_output
import flask
from flask import request, render_template, Markup, flash
import string, random, hashlib
from flaskext.bcrypt import Bcrypt

app = flask.Flask(__name__)
app.debug = True
bcrypt = Bcrypt(app)
db = shelve.open("shorten.db")
db2 = shelve.open("key.db")
user_db = shelve.open("users.db")

result_html_head = """{% extends "layout.html" %}{% block body %}<div class="starter-template"><h1>Done.</h1><p class="lead">"""
result_html_rest = """<br></p></div>{% endblock %}"""
HOST = 'http://localhost:5000'

badpage = """<html><head><title>Results</title></head><body>    <h1>Sorry, your request is not valid.</h1><div><a href="/home"></a></div></body></html>"""

tweet_link = '<a href="https://twitter.com/share" class="twitter-share-button" data-lang="en">Tweet</a>'

@app.route('/login', methods=['POST'])
def login():
    username = str(request.form["username"])
    password = str(request.form["password"])
    try:
        if user_db[username]==None or not bcrypt.check_password_hash(password, user_db[username]):
            #wrong password
            flash(u'Wrong username or password', 'error')
            return render_template("home.html")
        else:
            #successful login
            return render_template("home.html")
    except Exception, e:
        #wrong Username
        flash(u'Wrong username','error')
        return render_template("home.html")


@app.route('/developers', methods=['GET'])
def showDevelopers():
    return render_template("developers.html")

@app.route('/signup', methods=['GET'])
def showSignup():
    return render_template("signup.html")



@app.route('/server/shorts', methods=['POST'])
def addingUrl():
    if request.method == 'POST':
        key = request.form["short"]
        value = request.form["long"]
        if not isValid(value):
            value = 'http://' + value
        db[str(key)]=value
        app.logger.debug("SET: key ="+key)
        app.logger.debug("SET: value =" + value)
        #return flask.render_template('home.html')

        return return_response(key,value)
    else:
        return badpage

def isValid(url):
    return url[:4] == 'http'

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
    
    # if we vae the url in db
    if db2.has_key(str(value)):
        return return_response(db2[str(value)],value)   
    # find a unique key
    while(db.has_key(str(key))):
        key = link_generator()

    user_email = ''

    #add find user in session

    if user_email != '':
        user_db[str(user_email)]["urls"].append((key, value))
    db[str(key)]   = value
    db2[str(value)] = key
    
    #return flask.render_template('home.html')
    return return_response(str(key),str(value))

def loggedIn():
    pass

@app.route('/server/createUser', methods=['POST'])
def createUser():
    if not "counter" in user_db.keys():
        user_db["counter"] = 0

    email = request.form["user_email"]
    password = request.form["password"]

    # if we vae the url in user_db
    #if user_db.has_key(str(email)):
    #   pass
    if user_db.get(str(email)) is not None:
        flash(u'Wrong username or password', 'error')
        return render_template("signup.html")
 
    user_db[str(email)] = {'password': bcrypt.generate_password_hash(password), 'id': user_db['counter'], "urls":[]}
    user_db['counter']+=1

    #return flask.render_template('home.html')
    return return_user(str(email))

def return_user(k):
    res = result_html_head+'Successfully created user ' + k + " " +result_html_rest
    return flask.render_template_string(res)
    
def return_response(k,v):
    #res = result_html_head+'Now you can use <a href="'+HOST+'/server/short/'+k+'">'+HOST+'/server/short/'+k+'</a><br> instead of '+v+result_html_rest
    res = result_html_head + """
        Now you can use <a target="_blank" href='"""+HOST+"""/server/short/"""+k+"""'>"""+HOST+"""/server/short/"""+k+"""</a><br> instead of """+v+"""
        <br><br>
        Or, tweet your shortened URL!
        <br>
        <a href='https://twitter.com/share?text="""+HOST+"""/server/short/"""+k+"""' class='twitter-share-button' data-lang='en'>Tweet</a>
        <script>
            !function(d,s,id){
                var js,fjs=d.getElementsByTagName(s)[0];
                if(!d.getElementById(id)){
                    js=d.createElement(s);
                    js.id=id;
                    js.src='https://platform.twitter.com/widgets.js';
                    fjs.parentNode.insertBefore(js,fjs);
                }
            }(document,'script','twitter-wjs');
        </script>
        """ + result_html_rest
    return flask.render_template_string(res)

@app.route('/server/short/<key>', methods=['GET'])
def getUrl(key):

    
    value = db.get(str(key))
    if value is not None:
        return flask.redirect(value) 
    else:
        return render_template('404.html'), 404
    

    '''
    try:
        value = db.get(str(key))
        app.logger.debug("key was "+key)
        app.logger.debug("Redirecting to " + value)
        return flask.redirect(value)    

    except Exception, e:
        return render_template('404.html'), 404
    else:
        pass
    '''
    
def link_generator(size=6, chars=string.ascii_uppercase + string.digits + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

###
# Home Resource:
# Only supports the GET method, returns a homepage represented as HTML
###
@app.route('/home', methods=['GET'])
def home():
    """Builds a template based on a GET request, with some default
    arguements"""
    index_title = request.args.get("title", "i253")
    hello_name = request.args.get("name", "Jim")
    return flask.render_template(
            'home.html',
            title=index_title,
            name=hello_name)

if __name__ == "__main__":
    app.run(port=5000)
