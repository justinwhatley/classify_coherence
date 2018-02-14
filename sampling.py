import os
import random
import csv
import json

MECHANICAL_TURKS_DIR = "mechanical_turks_input_data"
CROWDFLOWER_DIR = "crowdflower_input_data"

def prepare_sample_for_crowdflower():

    open(CROWDFLOWER_DIR + "/samples.csv", 'w') # Clear contents of file
    # Get txt version of data
    with open(CROWDFLOWER_DIR + "/samples.csv", 'a+') as csvfile:
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
    column_list.append(dataset)
    while counter <= questions_per_hit:
        column_list.append(sample_template + str(counter) + '_' + str(1))
        column_list.append(sample_template + str(counter) + '_' + str(2))
        column_list.append(incoherent_sample_template + str(counter))
        counter += 1

    writer.writerow(column_list)
    exit(0)
    return csvfile, writer

def get_random_sample(sample_size, population_size):
    return random.sample(range(1, population_size), sample_size)


def get_original_sentence(coherent_data, incoherent_data_line):
    # Gets the original sentence which was corrupted
    print connect_sentence(incoherent_data_line)
    print connect_sentence(coherent_data[incoherent_data_line['OriginalSentenceIndex']])
    return connect_sentence(coherent_data[incoherent_data_line['OriginalSentenceIndex']])

def remove_long_sentence_pairs(length):
    pass


def write_csv_data_basic(sample_name, sample_directory, sample_size, coherent_data, incoherent_data, filename):
    """
    Writes one coherent/incoherent pair per row
    """
    # Erases and sets up a new CSV file, returning handles
    csvfile, writer = setup_csv_basic(sample_name, sample_directory)

    # Insert from sampling module
    population_size = len(incoherent_data)
    sample_list = get_random_sample(sample_size, population_size)

    counter = 0
    for i, line in enumerate(incoherent_data):
        if i in sample_list:
            counter += 1
            incoherent_sentence = connect_sentence(line).encode('ascii', 'ignore')
            coherent_sentence = get_original_sentence(coherent_data, line).encode('ascii', 'ignore')
            incoherent_selection = random.randint(0, 1)
            if incoherent_selection:
                writer.writerow([filename, coherent_sentence, incoherent_sentence, incoherent_selection + 1])
            else:
                writer.writerow([filename, incoherent_sentence, coherent_sentence, incoherent_selection + 1])
            sample_list.remove(i)
            if len(sample_list) == 0:
                break

    csvfile.close()


def write_csv_data_multi_question_hit(sample_name, sample_directory, sample_size, coherent_data, incoherent_data, filename, questions_per_hit):
    """
    Creates additional sample columns to include a number of coherent/incoherent per row (based on the number of
    questions_per_HIT. This allows many questions to be loaded in an amazon MT questionnaire (aka HIT)
    """

    # Erases and sets up a new CSV file, returning handles
    csvfile, writer = setup_csv_multi_question_hit(sample_name, sample_directory, questions_per_hit)

    # Insert from sampling module
    population_size = len(incoherent_data)
    sample_list = get_random_sample(sample_size, population_size)

    #add to list of csv
    for i, line in enumerate(incoherent_data):
        if i in sample_list:
            incoherent_sentence = connect_sentence(line).encode('ascii', 'ignore')
            coherent_sentence = get_original_sentence(coherent_data, line).encode('ascii', 'ignore')
            incoherent_selection = random.randint(0, 1)
            if incoherent_selection:
                writer.writerow([filename, coherent_sentence, incoherent_sentence, incoherent_selection + 1])
            else:
                writer.writerow([filename, incoherent_sentence, coherent_sentence, incoherent_selection + 1])
            sample_list.remove(i)
            if len(sample_list) == 0:
                break


def prepare_coherent_incoherent_pair_sample(sample_name, sample_directory, sample_size, questions_per_hit = 1):

    # Loads data for the uncorrupted sentences
    coherent_data = []
    coherent_json_filename = "coherent_sentences.json"
    for line in open(os.path.join("data/json/",coherent_json_filename), 'r'):
        coherent_data.append(json.loads(line))

    for filename in os.listdir(os.getcwd() + "/data/json"):
        # Variables for file-specific data
        if filename in [".keep", coherent_json_filename]:
            continue

        # Loads data for the corrupted sentences
        incoherent_data = []
        for line in open(os.path.join("data/json/",filename), 'r'):
            incoherent_data.append(json.loads(line))

        if questions_per_hit == 1:
            write_csv_data_basic(sample_name, sample_directory, sample_size, coherent_data, incoherent_data, filename)
        else:
            write_csv_data_multi_question_hit(sample_name, sample_directory, sample_size, coherent_data, incoherent_data, filename, questions_per_hit)

            
if __name__ == '__main__':
    sample_name = "samples.csv"
    sample_directory = MECHANICAL_TURKS_DIR
    sample_size = 10
    questions_per_hit = 10
    prepare_coherent_incoherent_pair_sample(sample_name, sample_directory, sample_size, questions_per_hit)
