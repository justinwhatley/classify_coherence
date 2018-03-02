from myapp import app
import flask
from flask import redirect, render_template, flash
from flask_login import login_required, current_user, login_manager
from flask import request
from os.path import join
from wtforms import Form, TextField, Field, validators, StringField, SubmitField


from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

sample_directory = 'mechanical_turks_input_data'
sample_name = 'Batch_3118690_samples.csv'
sample = join(sample_directory, sample_name)
import csv
def read_csv():
    """
    Loads the csv data by row, assigning each row value to a column key
    :return:
    """

    csv_list_of_dicts = []
    with open(sample, 'rb') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        header = None
        for i, row_list in enumerate(reader):
            if i == 0:
                header = row_list
            else:
                result_obj = {}
                for j, result in enumerate(row_list):
                    result_obj[header[j]] = row_list[j]
                csv_list_of_dicts.append(result_obj)

    return csv_list_of_dicts

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


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)



class ReusableForm(Form):
    name = TextField('Name:', validators=[validators.required()])


@app.route("/test", methods=['GET', 'POST'])
def hello():
    form = ReusableForm(request.form)

    print form.errors
    if request.method == 'POST':
        name = request.form['name']
        print name

        if form.validate():
            # Save the comment here.
            flash('Hello ' + name)
        else:
            flash('All the form fields are required. ')

    return render_template('hello.html', form=form)

csv_list_of_dicts = read_csv()
@app.route("/hit1", methods=['GET', 'POST'])
@login_required
def hit1():
    form = ReusableForm(request.form)

    request.form[render_template('hit_template.html', dict = csv_list_of_dicts[0])]

    print('made it')
    print form.errors
    if request.method == 'POST':
        name = request.form['name']
        print name

    return render_template('hit_template.html', dict = csv_list_of_dicts[0])

# @app.route("/handle_result", methods=['POST'])
# def handle_data():
#     print('made it')
#     projectpath = request.form['/handle_result']
#     print projectpath
#
#     print(request.form['submit_result'])


@app.route("/hit2", methods=['POST'])
def hit2():
    return render_template('hit_template.html', dict = csv_list_of_dicts[1])
#
# csv_list_of_dicts = read_csv()
# @app.route("/hit3", methods=['POST', 'GET'])
# def hit3():
#     return render_template('hit_template.html', dict = csv_list_of_dicts[2])
#
# @app.route("/hit4", methods=['POST', 'GET'])
# def hit4():
#     return render_template('hit_template.html', dict = csv_list_of_dicts[3])
#
# csv_list_of_dicts = read_csv()
# @app.route("/hit5", methods=['POST', 'GET'])
# def hit5():
#     return render_template('hit_template.html', dict = csv_list_of_dicts[4])
#
# @app.route("/hit6", methods=['POST', 'GET'])
# def hit6():
#     return render_template('hit_template.html', dict = csv_list_of_dicts[5])
#
# @app.route("/hit7", methods=['POST', 'GET'])
# def hit7():
#     return render_template('hit_template.html', dict = csv_list_of_dicts[6])
#
# @app.route("/hit8", methods=['POST', 'GET'])
# def hit8():
#     return render_template('hit_template.html', dict = csv_list_of_dicts[7])
#
# @app.route("/hit9", methods=['POST', 'GET'])
# def hit9():
#     return render_template('hit_template.html', dict = csv_list_of_dicts[8])

# TODO other functions