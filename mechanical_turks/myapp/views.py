from myapp import app
import flask
from flask import redirect, render_template, flash
from flask_login import login_required, current_user, login_manager
from flask import request
from os.path import join
from wtforms import Form, TextField, Field, validators, StringField, SubmitField


from myapp.api import csv_list_of_dicts
from myapp.api import User

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


# Handles user login
login_manager = login_manager.LoginManager()
login_manager.init_app(app)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class Continue(FlaskForm):
    submit = SubmitField('Continue')


@app.route('/', methods=['POST', 'GET'])
def home():
    form = Continue()
    if request.method == 'POST':
        if request.form['submit']:
            return login()
    return render_template('index.html', form=form)



# @app.route('/login')
# def login():
#     form = LoginForm()
#     if request.method == 'POST':
#         if request.form['submit']:
#             print('made it')
#             # print form.username
#             # print form.password
#     return render_template('login.html', title='Sign In', form=form)
users = {'justin': {'password': '1234'}}


@login_manager.user_loader
def user_loader(user_name):
    if user_name not in users:
        return

    user = User()
    user.id = email
    return user

@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form['password'] == users[email]['password']

    return user
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm()
    if form.validate_on_submit():
        # Login and validate the user.
        # user should be an instance of your `User` class
        login_user(user)

        flask.flash('Logged in successfully.')

        next = flask.request.args.get('next')
        # is_safe_url should check if the url is safe for redirects.
        # See http://flask.pocoo.org/snippets/62/ for an example.
        if not is_safe_url(next):
            return flask.abort(400)

        return flask.redirect(next or flask.url_for('index'))
    return flask.render_template('login.html', form=form)

from urlparse import urlparse, urljoin
from flask import request, url_for

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc



"""
-----------------------------------------------------------------------------------------------------------------------
HIT form submissions 


-----------------------------------------------------------------------------------------------------------------------
"""


@app.route("/hit<int:number>", methods=['GET', 'POST'])
def hit(number):
    """
    Generates the questionnaire for a given number
    :param number:
    :return:
    """
    if request.method == 'POST':
        result = request.form
        #Assumes a full HIT of ten
        for key in result:
            print (key, result[key])
        return redirect(url_for('hit', number=number+1))

    if not (1 <= number <= 7):
        return 'Out of bounds!'
    print(number)
    return render_template('hit_template.html', dict=csv_list_of_dicts[number], SubmitForm='/hit'+str(number))


@app.route("/handle_result", methods=['GET','POST'])
def handle_data():
    if request.method == 'POST':
        result = request.form
        for key in result:
            print (key, result[key])

    return render_template('hit_template.html', dict=csv_list_of_dicts[5])

