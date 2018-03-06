import flask
from flask_sqlalchemy import SQLAlchemy

app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
# app.config.from_object(os.environ['APP_SETTINGS'])
app.config["DEBUG"] = True
app.config["SECRET_KEY"] = 'a very long random string'


db = SQLAlchemy(app)

from myapp import api
from myapp import views
from myapp import models
