from myapp import app
from flask import redirect, render_template, flash, url_for
from flask import redirect, render_template, flash
from flask_login import login_required, current_user
from flask import request


from myapp.api import csv_list_of_dicts, write_line_to_csv
from myapp.api import Continue, LoginForm, RegistrationForm


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
from myapp.api import User, new_user

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        result = request.form
        if result['password'] != result['password2']:
            flash('Passwords do not match')
            return render_template('register_user.html', title='Sign In', form=form)
        else:
            success = new_user(result)
            if success:
                return redirect(url_for('hit', number=1, username =success['username']))

    return render_template('register_user.html', title='Sign In', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    #TODO connect with authentication functions in api
    # if current_user.is_authenticated:
    #     print('made it')
    #     return redirect(url_for('hit', number=1))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))


    return render_template('login.html', title='Sign In', form=form)


# with app.test_request_context():
#     print url_for('index')
#     print url_for('login')
#     print url_for('login', next='/')
#     print url_for('profile', username='John Doe')


"""
********************************************************************************************
HIT Form Handling
********************************************************************************************
"""

# @app.route("/hit<int:number>/<username>", methods=['GET', 'POST'])
@app.route("/hit<int:number>/<username>", methods=['GET', 'POST'])
def hit(number, username):
    """
    Generates the questionnaire for a given number
    :param number:
    :return:
    """
    if request.method == 'POST':
        result = request.form
        #Assumes a full HIT of ten
        write_line_to_csv(result, number)
        return redirect(url_for('hit', number=number+1, username= username))
        # return render_template('hit_template.html', dict=csv_list_of_dicts[number], SubmitForm='/hit'+str(number+1))

    if not (1 <= number <= 7):
        return 'Out of bounds!'
    print(csv_list_of_dicts[number])
    print(number)
    return render_template('hit_template.html', dict=csv_list_of_dicts[number], SubmitForm='/hit'+str(number))


# @app.route("/handle_result", methods=['GET','POST'])
# def handle_data():
#     if request.method == 'POST':
#         result = request.form
#         for key in result:
#             print (key, result[key])
#
#     return render_template('hit_template.html', dict=csv_list_of_dicts[5])

"""
********************************************************************************************
********************************************************************************************
"""