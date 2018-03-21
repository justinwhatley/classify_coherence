import flask
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth

app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
# app.config.from_object(os.environ['APP_SETTINGS'])
# app.config["DEBUG"] = False
app.config["SECRET_KEY"] = 'a very long random string'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

# extensions
auth = HTTPBasicAuth()
db = SQLAlchemy(app)

from myapp import api
from myapp import views
from myapp import models
