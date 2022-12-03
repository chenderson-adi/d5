#Created 6/30/2022 - CSH demo started from url
#


#                 HTML Templates         Need for routes        need for dynamic query = ?        return json    need for redirect    need for redirect
from flask import Blueprint,           render_template,               request,                    jsonify,        redirect,           url_for


views = Blueprint(__name__, "index")

@views.route("/")
def index ():
    return render_template('index.html')
    

@views.route('/profile')
def profile():
    return render_template('profile.html')

@views.route('/login')
def login():
    return 'Login'

@views.route('/signup')
def signup():
    return 'Signup'

@views.route('/logout')
def logout():
    return 'Logout'

















#@views.route("/")
#def home ():
#    #return "home page"
#    return render_template("tindex.html",name = "Dickhead" )


#example of dynamic query parameter 
#Usage = #Default usage -- #http://127.0.0.1:8000/views/profile/craig
@views.route("/profile1/<username>")
def profile1(username):
    return render_template("tprofile.html", name=username)  #note the use of a diffent page

#example of dynamic query parameter 
#usage =    http://127.0.0.1:8000/views/profile2?name=assjack
@views.route("/profile2")
def profile2():
    args = request.args
    name = args.get('name')
    return render_template("tindex.html", name=name)  
#return json
#http://127.0.0.1:8000/views/json
#If accessed from javascript, it would return a JSON object, html shows text
@views.route("/json")
def get_json():
    return jsonify({'name': 'assjack', 'weight': 200})

#if someone wants to send data from json (this example does nothing)
@views.route("/data")
def get_data():
    data = request.json
    return jsonify(data)

#redirect a page
@views.route("/go-to-home")
def go_to_home():
    return redirect(url_for("views.home"))