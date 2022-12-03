#Created 6/30/2022 - CSH demo started from url
#https://www.youtube.com/watch?v=kng-mJJby8g
#https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login#step-2-creating-the-main-app-file
from flask import Flask
from views import views
from main import main
from flask_sqlalchemy import SQLAlchemy


app= Flask(__name__)
app.register_blueprint(views, url_prefix="/index" )

app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
   

if __name__=='__main__':
    app.run(debug=True, port=8000)


    