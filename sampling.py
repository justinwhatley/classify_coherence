import os
import random
import csv
import json

mechanical_turks_dir = 'mechanical_turks'
mechanical_turks_input_dir = 'mechanical_turks_input_data'
MECHANICAL_TURKS_DIR = os.path.join(mechanical_turks_dir, mechanical_turks_input_dir)

CROWDFLOWER_DIR = "crowdflower_input_data"

def prepare_sample_for_crowdflower():

    open(CROWDFLOWER_DIR + "/Batch_3118690_samples.csv", 'w') # Clear contents of file
    # Get txt version of data
    with open(CROWDFLOWER_DIR + "/Batch_3118690_samples.csv", 'a+') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Dataset", "Sample1", "Sample2", "CoherentSentence", "IncoherentSentence"])
        for filename in os.listdir(os.getcwd()+ "/data/txt"):

            if filename in [".keep", "coherent_sentences.txt"]:
                continue

            filepath = "data/txt/" + filename
            print('Filepath: ' + filepath)
            num_lines = sum(1 for line in open(filepath, 'r'))
            print(num_lines)

            # Randomly get 51 lines in the file
            sample_lines = random.sample(range(1, num_lines), 51)

            i = 0
            for line in open(filepath, 'r'):
                if i in sample_lines:
                    writer.writerow([filename, line])
                    sample_lines.remove(i)
                i += 1

def first_char_to_lower(str):
    """
    First char is put to a lower case, if it isn't already
    """
    if str[0].isupper():
        str = str[:1].lower() + str[1:]
    return str

def first_char_to_upper(str):
    """
    First char is put to a upper case, if it isn't already
    """
    if str[0].islower():
        str = str[:1].upper() + str[1:]
    return str

def connect_sentence(line, include_connective = True):
    # Convert to raw text

    if include_connective:
        sentence = line['Arg1Raw'] + ". " \
                   + first_char_to_upper(line['ConnectiveRaw']) + " " \
                   + first_char_to_lower(line['Arg2Raw'] + ". " + "\n")
    else:
        sentence = line['Arg1Raw'] + ". " + line['Arg2Raw'] + ". " + "\n"
    return sentence


def setup_csv_basic(sample_name, sample_directory):
    """

    :param sample_name:
    :param sample_directory:
    :return:
    """

    file_location = os.path.join(sample_directory, sample_name)
    # Clear contents of file
    f = open(file_location, 'w+')
    f.close()
    # Get txt version of data
    csvfile = open(file_location, 'a+')
    writer = csv.writer(csvfile)
    # Generate header information
    dataset = "Dataset"
    sample1 = "Sample1"
    sample2 = "Sample2"
    incoherent_sample = "Incoherent_Sample"
    writer.writerow([dataset, sample1, sample2, incoherent_sample])
    return csvfile, writer

def setup_csv_multi_question_hit(sample_name, sample_directory, questions_per_hit):

    file_location = os.path.join(sample_directory, sample_name)
    # Clear contents of file
    f = open(file_location, 'w+')
    f.close()
    # Get txt version of data
    csvfile = open(file_location, 'a+')
    writer = csv.writer(csvfile)
    # Generate header information

    dataset = "Dataset"
    sample_template = "Sample"
    incoherent_sample_template = "Incoherent_Sample"

    counter = 1
    column_list = []
    while counter <= questions_per_hit:
        sample = sample_template + str(counter)
        column_list.append(sample + dataset)
        column_list.append(sample + '_' + str(1))
        column_list.append(sample + '_' + str(2))
        column_list.append(incoherent_sample_template + str(counter))
        counter += 1

    writer.writerow(column_list)
    return csvfile, writer

def get_random_sample(sample_size, population_size):
    return random.sample(range(1, population_size), sample_size)


def get_original_sentence(coherent_data, incoherent_data_line):
    # Gets the original sentence which was corrupted
    # print connect_sentence(incoherent_data_line)
    # print connect_sentence(coherent_data[incoherent_data_line['OriginalSentenceIndex']])
    return connect_sentence(coherent_data[incoherent_data_line['OriginalSentenceIndex']])

def is_longer_than_length_limit(sentence, length_limit, length_type):
    # Gets sample length based on the length type considered
    if length_type == 'char':
        sample_length = len(sentence)
    elif length_type == 'word':
        sample_length = len(sentence.split())

    if sample_length >= length_limit:
        return True
    return False


def generate_random_sentence_pairs(sample_size, coherent_data, incoherent_data, filename):
    # Insert from sampling module
    population_size = len(incoherent_data)
    sample_list = get_random_sample(sample_size, population_size)

    sample_pair_list = []
    for i, line in enumerate(incoherent_data):
        if i in sample_list:
            incoherent_sentence = connect_sentence(line).encode('ascii', 'ignore')
            # print len(incoherent_sentence.split()) >= 35
            coherent_sentence = get_original_sentence(coherent_data, line).encode('ascii', 'ignore')
            # print len(coherent_sentence.split()) >= 35

            incoherent_selection = random.randint(0, 1)
            if incoherent_selection:
                sample_pair_list.append([filename, coherent_sentence, incoherent_sentence, incoherent_selection + 1])
            else:
                sample_pair_list.append([filename, coherent_sentence, incoherent_sentence, incoherent_selection + 1])
            sample_list.remove(i)
            if len(sample_list) == 0:
                break

    return sample_pair_list

def write_csv_data_basic(sample_name, sample_directory, sample_pair_list):
    """
    Writes one coherent/incoherent pair per row
    """
    # Erases and sets up a new CSV file, returning handles
    csvfile, writer = setup_csv_basic(sample_name, sample_directory)

    for row in sample_pair_list:
        writer.writerow(row)

    csvfile.close()


def write_csv_data_multi_question_hit(sample_name, sample_directory, questions_per_hit, sample_pair_list):
    """
    Creates additional sample columns to include a number of coherent/incoherent per row (based on the number of
    questions_per_HIT. This allows many questions to be loaded in an amazon MT questionnaire (aka HIT)
    """

    # Erases and sets up a new CSV file, returning handles
    csvfile, writer = setup_csv_multi_question_hit(sample_name, sample_directory, questions_per_hit)

    counter = 1
    column_list = []
    for row in sample_pair_list:
        column_list = column_list + row
        if counter % questions_per_hit == 0:
            writer.writerow(column_list)
            column_list = []
        counter += 1


def prepare_coherent_incoherent_pair_sample(sample_name, sample_directory, sample_size, questions_per_hit = 1, length_limit = None , length_type = 'word', specify_datasets = None):

    # Loads data for the uncorrupted sentences
    coherent_data = []
    coherent_json_filename = "coherent_sentences.json"
    for line in open(os.path.join("data/json/",coherent_json_filename), 'r'):
        coherent_data.append(json.loads(line))

    if not specify_datasets:
        datasets = os.listdir(os.getcwd() + "/data/json")
    else:
        datasets = specify_datasets

    sample_pair_list = []
    for filename in datasets:
        # Variables for file-specific data
        if filename in [".keep", coherent_json_filename]:
            continue

        # Loads data for the corrupted sentences
        incoherent_data = []
        for line in open(os.path.join("data/json/",filename), 'r'):
            incoherent_data.append(json.loads(line))
            if length_limit:
                line = incoherent_data.pop()
                # ensures that neither the incoherent or coherent sentence will be too long
                incoherent_sentence = connect_sentence(line).encode('ascii', 'ignore')
                coherent_sentence = get_original_sentence(coherent_data, line).encode('ascii', 'ignore')
                one_of_pair_too_long = is_longer_than_length_limit(incoherent_sentence, length_limit, length_type) or \
                                       is_longer_than_length_limit(coherent_sentence, length_limit, length_type)
                if not one_of_pair_too_long:
                    incoherent_data.append(line)

        sample_pair_list = sample_pair_list + generate_random_sentence_pairs(sample_size, coherent_data, incoherent_data, filename)

    random.shuffle(sample_pair_list)
    if questions_per_hit == 1:
        write_csv_data_basic(sample_name, sample_directory, sample_pair_list)
    else:
        write_csv_data_multi_question_hit(sample_name, sample_directory, questions_per_hit, sample_pair_list)

def ensure_correct_sample_size_to_questions_per_hit_ratio(sample_size_per_dataset, questions_per_hit, specify_datasets=None):
    """
    The number of questions_per_HIT must be a factor of the number of samples drawn from all datasets.
    Otherwise, there will be one incomplete HIT. The samples CSV was not generated.. Not including this questionnaire
    (another possible solution) would mean potentially uneven sampling from each dataset as these are being presented
    throughout the questionnaires randomly
    """

    if not specify_datasets:
        datasets = os.listdir(os.getcwd() + "/data/json")
    else:
        datasets = specify_datasets

    error_message = "The number of questions_per_HIT must be a factor of the number of samples drawn from all datasets. " \
                    "Otherwise, there will be one incomplete HIT. The samples CSV was not generated."
    if not (len(datasets) * sample_size_per_dataset) % questions_per_hit == 0:
        print error_message
        exit(0)

def test_csv_sample():
    path = 'mechanical_turks_input_data/Batch_3118690_samples.csv'

    with open(path, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader):
            # print row
            # for keys in row:
            #     print keys
            # break

            # Single question per HIT
            # if row['Sample1'] == row['Sample2']:
            #     print 'duplicate'

            # Multiple questions per HIT
            for i in range(1, 10):
                if row['Sample' + str(i) + "_" + str(1)] == row['Sample' + str(i) + "_" + str(2)]:
                    print 'DUPLICATE!!'
                    exit(0)

                incoherent_sample_key = 'Sample' + str(i) + "_" + row['Incoherent_Sample' + str(i)]
                print ('The incoherent sample is: ' + incoherent_sample_key)
                print "1. " + row['Sample' + str(i) + "_" + str(1)]
                print "2. " + row['Sample' + str(i) + "_" + str(2)]


def add_time_stamp(fname, fmt='%Y_%m_%d_%H_%M_{fname}'):
    """
    Adds the date to front of a string
    :param fname:
    :param fmt:
    :return:
    """
    import datetime
    return datetime.datetime.now().strftime(fmt).format(fname=fname)

if __name__ == '__main__':

    sample_name = add_time_stamp("sample.csv")
    sample_directory = MECHANICAL_TURKS_DIR

    print('Writing to: ' )
    print(os.path.join(MECHANICAL_TURKS_DIR, sample_name))

    sample_size_per_dataset = 20
    questions_per_hit = 10


    print('Taking '+ str(sample_size_per_dataset) + ' sentence pairs from each dataset')
    print('with ' + str(questions_per_hit) + ' questions per questionnaire')

    length_limit = 35
    length_type = 'word'

    # specify_datasets = ['incoherent_sentences_arg2_diff_sense.json', 'incoherent_sentences_arg2_random.json']
    # ensure_correct_sample_size_to_questions_per_hit_ratio(sample_size_per_dataset, questions_per_hit, specify_datasets)
    # prepare_coherent_incoherent_pair_sample(sample_name, sample_directory, sample_size_per_dataset, questions_per_hit, specify_datasets)

    ensure_correct_sample_size_to_questions_per_hit_ratio(sample_size_per_dataset, questions_per_hit)
    prepare_coherent_incoherent_pair_sample(sample_name, sample_directory, sample_size_per_dataset, questions_per_hit, length_limit = length_limit, length_type = 'word')