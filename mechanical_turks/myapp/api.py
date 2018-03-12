import flask

# New modules
import flask_sqlalchemy
import flask_restless
import flask_login

from myapp import app, db
from myapp.models import User

# Create the Flask-Restless API manager.
manager = flask_restless.APIManager(app, flask_sqlalchemy_db=db)

# Create login manager
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.
manager.create_api(User, methods=['GET', 'POST', 'DELETE'])


def read_csv():
    import csv
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

def write_line_to_csv(form_response, form_number):
    pass

sample_directory = 'mechanical_turks_input_data'
sample_name = 'Batch_3118690_samples.csv'
from os.path import join
sample = join(sample_directory, sample_name)
csv_list_of_dicts = read_csv()


class User(flask_login.UserMixin):
    def __init__(self, name, id, active=True):
        self.name = name
        self.id = id
        self.active = active

    def is_active(self):
        # Here you should write whatever the code is
        # that checks the database if your user is active
        return self.active

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True