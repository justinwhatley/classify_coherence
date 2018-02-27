from myapp import app
from flask import redirect, render_template
from flask import request
from os.path import join

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


@app.route('/', methods=['POST', 'GET'])
def login():
    error = None
    # if request.method == 'POST':
    #     if valid_login(request.form['username'],
    #                    request.form['password']):
    #         return log_the_user_in(request.form['username'])
    #     else:
    #         error = 'Invalid username/password'
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return render_template('index.html', error=error)


csv_list_of_dicts = read_csv()
@app.route("/hit1", methods=['POST', 'GET'])
def hit1():
    return render_template('hit_template.html', dict = csv_list_of_dicts[0])

@app.route("/hit2", methods=['POST', 'GET'])
def hit2():
    return render_template('hit_template.html', dict = csv_list_of_dicts[1])

csv_list_of_dicts = read_csv()
@app.route("/hit3", methods=['POST', 'GET'])
def hit3():
    return render_template('hit_template.html', dict = csv_list_of_dicts[2])

@app.route("/hit4", methods=['POST', 'GET'])
def hit4():
    return render_template('hit_template.html', dict = csv_list_of_dicts[3])

csv_list_of_dicts = read_csv()
@app.route("/hit5", methods=['POST', 'GET'])
def hit5():
    return render_template('hit_template.html', dict = csv_list_of_dicts[4])

@app.route("/hit6", methods=['POST', 'GET'])
def hit6():
    return render_template('hit_template.html', dict = csv_list_of_dicts[5])

@app.route("/hit7", methods=['POST', 'GET'])
def hit7():
    return render_template('hit_template.html', dict = csv_list_of_dicts[6])

@app.route("/hit8", methods=['POST', 'GET'])
def hit8():
    return render_template('hit_template.html', dict = csv_list_of_dicts[7])

@app.route("/hit9", methods=['POST', 'GET'])
def hit9():
    return render_template('hit_template.html', dict = csv_list_of_dicts[8])

# TODO other functions