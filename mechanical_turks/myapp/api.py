import flask

#!/usr/bin/env python

# New modules
import flask_sqlalchemy
import flask_restless
import flask_login
from flask import flash

from myapp import app, db, auth
from myapp.models import User, Completed_Questionnaires

# Create the Flask-Restless API manager.
manager = flask_restless.APIManager(app, flask_sqlalchemy_db=db)

# Create login manager
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.
manager.create_api(User, methods=['GET', 'POST', 'DELETE'])
manager.create_api(Completed_Questionnaires, methods=['GET', 'POST', 'DELETE'])


"""
********************************************************************************************
Form handling
********************************************************************************************
"""
from wtforms import Form, TextField, Field, validators, StringField, SubmitField
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email

class RegistrationForm(FlaskForm):
    username = StringField('Email', validators=[DataRequired(), Email(message='Must be a valid email format')])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Create User')
    # login = SubmitField('Login')

class LoginForm(FlaskForm):
    username = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class Continue(FlaskForm):
    submit = SubmitField('Continue')

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))

"""
********************************************************************************************
User authentication
Ref. https://github.com/miguelgrinberg/REST-auth
********************************************************************************************
"""

@login_manager.user_loader
def load_user(username):
    return User.query.filter_by(username=username).first()

from flask import abort, request, jsonify, g, url_for

@auth.verify_password
def verify_password(username_or_token, password):
   # first try to authenticate by token
   user = User.verify_auth_token(username_or_token)
   if not user:
       # try to authenticate with username/password
       user = User.query.filter_by(username=username_or_token).first()
       if not user or not user.verify_password(password):
           return False
   g.user = user
   return True

# @app.route('/api/users', methods=['POST'])
def new_user(request):
    username = request.get('username')
    password = request.get('password')
    if username is None or password is None:
        flash('Username or password are not set')
        print('Username or password are not set')
        return False
        # abort(400)    # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        flash('User already exists')
        return False
        # abort(400)    # existing user
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()

    completed_questionnaires = Completed_Questionnaires(user_id=user.id, last_answered_question = 0)
    db.session.add(completed_questionnaires)
    db.session.commit()

    return get_user(id=user.id)
    # return (jsonify({'username': user.username}), 201,
    #        {'Location': url_for('get_user', id=user.id, _external=True)})

# @app.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return {'username': user.username}

@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})

@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.username})


"""
********************************************************************************************
CSV reading/writing for questionnaire presentation and result storage
********************************************************************************************
"""

import Queue
import thread, time
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
#TODO
sample_directory = 'mechanical_turks_input_data'
sample_name = 'Batch_3118690_samples.csv'
result_directory = 'local_server_output_data'
from os.path import join
sample = join(sample_directory, sample_name)
csv_list_of_dicts = read_csv()

# Warning - this implementation assumes the user of Flask's built-in server and NOT a production server
# other thread considerations may need to be taken in order to prevent race conditions on a production server
result_q = Queue.Queue(maxsize=100)

def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z

def write_line_to_csv(form_response, data_line, worker_id, hit_number):

    new_input_line = add_tag_to_key('Input.', csv_list_of_dicts[int(data_line)])
    new_output_line = add_tag_to_key('Answer.', form_response)
    new_line = merge_two_dicts(new_input_line, new_output_line)

    try:
        # Finds the appropriate user.id based on the worker_id(username) and adds the questionnaire to the completed table
        user = User.query.filter_by(username=worker_id).first()
        completed_q = Completed_Questionnaires.query.filter_by(user_id=user.id).first()
        setattr(completed_q, 'last_answered_question', hit_number)

        # adds user to response as 'WorkerId'
        new_line['WorkerId'] = worker_id
        result_q.put(new_line)

        db.session.commit()
    except:
        return False
    return True


def add_tag_to_key(tag, original_dict):
    temp_dict = {}
    for key in original_dict:
        temp_dict[tag + key] = original_dict[key]
    return temp_dict

def get_number_of_questions(csv_data):
    """
    Gets the largest sample number to determine the number of questions assigned per row (or per HIT)
    :param csv_data:
    :return:
    """
    largest_question_number = 1
    for key in csv_data[0]:
        if 'Dataset' in key and 'Sample' in key:
            lst = key.split('Sample')
            sample_number = int(lst[1].split('Dataset')[0])
            if sample_number > largest_question_number:
                largest_question_number = sample_number
    return largest_question_number

def write_header(result_file):

    csvfile = open(result_file, 'w')
    # Creating header
    global csv_list_of_dicts
    # Assumes that the csv_list_of_dicts will contain the same keys throughout
    new_input_line = add_tag_to_key('Input.', csv_list_of_dicts[0])
    temp_answer_dict = {}
    print(get_number_of_questions(csv_list_of_dicts))
    for i in range(1, get_number_of_questions(csv_list_of_dicts)+1):
        temp_answer_dict['Answer' + str(i)] = 'Placeholder'
        temp_answer_dict['FollowupAnswer' + str(i)] = 'Placeholder'
    new_output_line = add_tag_to_key('Answer.', temp_answer_dict)
    new_output_line['WorkerId'] = 'Placeholder'
    new_output_line['RejectionTime'] = 'Placeholder'
    new_output_line['CreationTime'] = 'Placeholder'
    new_output_line['AcceptTime'] = 'Placeholder'
    new_output_line['SubmitTime'] = 'Placeholder'
    new_output_line['HITId'] = 'Placeholder'
    new_output_line['RequesterFeedback'] = 'Placeholder'

    new_line = merge_two_dicts(new_input_line, new_output_line)
    fieldnames = sorted(key for key, val in new_line.iteritems())

    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    csvfile.close()

    return fieldnames

def result_writer():
    global result_directory
    import os.path

    # Creates a new output file when the file already exists
    i = 0
    while True:
        result_path = join(result_directory, 'result')
        if i == 0:
            to_check = result_path + '.csv'
        else:
            to_check = result_path + str(i) + '.csv'
        if not os.path.exists(to_check):
            break
        i += 1

    if i == 0:
        result_file = result_path + '.csv'
    else:
        result_file = result_path + str(i) + '.csv'

    fieldnames = write_header(result_file)
    while True:
        while not result_q.empty():
            my_dict = result_q.get()
            csvfile = open(result_file, 'a')
            writer = csv.DictWriter(csvfile, fieldnames)
            print('Writing..')
            writer.writerow(my_dict)
            csvfile.close()
        time.sleep(5)
thread.start_new_thread(result_writer, ())



# ********************************************************************************************
# ********************************************************************************************

