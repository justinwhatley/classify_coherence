from myapp import app
from flask import redirect, render_template, flash, url_for
from flask import redirect, render_template, flash, abort
from flask_login import login_required, current_user
from flask import request


from myapp.api import csv_list_of_dicts, write_line_to_csv
from myapp.api import Continue, LoginForm, RegistrationForm, flash_errors


"""
********************************************************************************************
Home page and login
********************************************************************************************
"""


# Handles user login
# login_manager = login_manager.LoginManager()
# login_manager.init_app(app)

@app.route('/', methods=['POST', 'GET'])
def index():
    form = Continue()
    if request.method == 'POST':
        if request.form['submit']:
            return register()
    return render_template('index.html', form=form)


from flask_login import login_user
from myapp.api import User, Completed_Questionnaires, new_user, get_user, get_auth_token

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    # for item in form:
    #     print (item, form[item])
    #TODO add descriptive errors on validation
    if form.validate_on_submit():
        flash_errors(form)
        result = request.form
        if result['password'] != result['password2']:
            flash('Passwords do not match')
            return render_template('register_user.html', title='Sign In', form=form)
        else:
            success = new_user(result)

            if success:
                return redirect(url_for('hit', number=1, username=success['username']))

    return render_template('register_user.html', title='Sign In', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # TODO handling of CSRF tokens with: http://flask.pocoo.org/snippets/3/

    #TODO connect with authentication functions in api
    # if current_user.is_authenticated:
    #     print('made it')
    #     return redirect(url_for('hit', number=1))
    form = LoginForm()
    if form.validate_on_submit():
        result = request.form
        user = User.query.filter_by(username=result['username']).first()
        password = result['password']

        if user is None or not user.verify_password(password):
            print('Invalid username or password')
            flash('Invalid username or password')
            return redirect(url_for('login'))
        # login_user(user, remember=form.remember_me.data)
        else:
            completed_questionnaire = Completed_Questionnaires.query.filter_by(user_id = user.id).first()
            return redirect(url_for('hit', number=completed_questionnaire.last_answered_question+1, username=user.username))

    return render_template('login.html', title='Sign In', form=form)


"""
********************************************************************************************
HIT Form Handling
********************************************************************************************
"""

@app.route("/hit<int:number>/<username>", methods=['GET', 'POST'])
def hit(number, username):
    """
    Generates the questionnaire for a given number
    :param number:
    :return:
    """
    # Assumes the questionnaire will have 8 sheets
    if number == 9:
        return render_template('hits_complete.html')
    if not 1 <= number <= 8:
        return redirect(url_for('index'))


    if request.method == 'POST':
        result = request.form
        #Assumes a full HIT of ten
        completed = write_line_to_csv(result, number, username, number)
        if not completed:
            return redirect(url_for('index'))
        return redirect(url_for('hit', number=number+1, username= username))
        # return render_template('hit_template.html', dict=csv_list_of_dicts[number], SubmitForm='/hit'+str(number+1))


    return render_template('hit_template.html', dict=csv_list_of_dicts[number], SubmitForm='/hit'+str(number))


"""
********************************************************************************************
********************************************************************************************
"""