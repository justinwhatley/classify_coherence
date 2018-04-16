#!/usr/bin/env python
from __future__ import division
import os.path as path
import glob
import csv


from datetime import datetime


crowdflower_output_directory = 'crowdflower_output_data'
local_server_output_directory = './local_server_output_data'
mechanical_turks_output_directory = 'mechanical_turks_output_data/multi_question_hit'
# mechanical_turks_output_directory = 'mechanical_turks_output_data/single_question_hit'

def read_csv():
    """
    Loads the csv data by row, assigning each row value to a column key
    :return:
    """
    global local_server_output_directory
    directory = local_server_output_directory
    csv_list_of_dicts = []
    for filename in glob.glob(path.join(directory, '*.csv')):
        with open(filename, 'rb') as csv_file:
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

def test_csv_sample():

    with open(path, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader):

            # Multiple questions per HIT
            for i in range(1, 10):
                incoherent_sample_key = 'Sample' + str(i) + "_" + row['Incoherent_Sample' + str(i)]
                print ('The incoherent sample is: ' + incoherent_sample_key)
                print "1. " + row['Sample' + str(i) + "_" + str(1)]
                print "2. " + row['Sample' + str(i) + "_" + str(2)]


def get_sentence_length_based_results(csv_data, agreement_threshold, length_type='word', aggregate = False):
    #TODO will need to fix this up to run with new CSV presentations

    # Adds the lengths of each sample to the dictionary according to the length_type considered
    for row_dict in csv_data:
        if length_type == 'char':
            row_dict['sample_length'] = len(row_dict['sample'])
        elif length_type == 'word':
            row_dict['sample_length'] = len(row_dict['sample'].split())

    # Sorts CSV data based on sample_length
    sorted_by_sample_len = sorted(csv_data, key=lambda k: k['sample_length'])

    size_of_dataset = float(len(csv_data))
    print(size_of_dataset)
    delimiter = size_of_dataset/float(2)
    print(delimiter)

    # Creates three bins based on sentence length
    bin1, bin2= [], []
    for i, dict in enumerate(sorted_by_sample_len):
        if i < delimiter:
            bin1.append(dict)
        # elif delimiter <= i < (2 * delimiter):
        #     bin2.append(dict)
        else:
            bin2.append(dict)

    bins = [bin1, bin2]
    if length_type == 'char':
        print('Character length: ')
    elif length_type == 'word':
        print('Number of words: ')

    categories_list = get_diff_values_from_category(csv_data, 'dataset')
    result_list = []
    for _bin in bins:
        result_list.append(get_bin_data(list(categories_list), bin=_bin, agreement_threshold=agreement_threshold, aggregate=aggregate))

    print(cluster_matching_datasets(list(categories_list), result_list, agreement_threshold=agreement_threshold))

def cluster_matching_datasets(categories_list, result_list, agreement_threshold=None):
    """
    This clusters different bin results based on the dataset the result belongs to
    :param categories_list:
    :param result_list:
    :param agreement_threshold:
    :return:
    """
    output = ""
    if agreement_threshold:
        output = "Agreement required for passing result: " + str(agreement_threshold)
    while (categories_list):
        to_check = categories_list.pop()
        output += "\n" + to_check + "\n"
        for dict in result_list:
            if agreement_threshold:
                output += output_percent_incoherence_with_annotator_agreement(dict, to_check, agreement_threshold)
            else:
                output += output_percent_incoherence(dict, to_check)
    return output


def output_percent_incoherence(dict, to_check):
    """
    Output function for the basic percent incoherence
    :param dict:
    :param to_check:
    :return:
    """
    return ("Percent Incoherent: " + str(
                dict[to_check]['bin_incoherence_freq'] / dict[to_check]['total_size'] * 100)
               + '\n')

def output_percent_incoherence_with_annotator_agreement(dict, to_check, agreement_threshold):
    """
    Output function for the percent incoherence based on annotator agreement
    :param dict:
    :param to_check:
    :param agreement_threshold:
    :return:
    """
    return ("Percent Incoherent at " + str(agreement_threshold) + " agreement: " +  str(
                dict[to_check]['incoherence_agreement'][0] / dict[to_check]['incoherence_agreement'][1] * 100)
            + " (" + str(dict[to_check]['incoherence_agreement'][0]) + " labelled incoherent at agreement rate out of "
            + str(dict[to_check]['incoherence_agreement'][1]) + " possible)"
            + '\n')

def get_bin_data(_bin, categories_list, agreement_threshold, aggregate=False):
    """
    Prints text length ranges as well as the percent of responses that were evaluated as incoherent
    :param _bin:
    :return:
    """

    result = {}
    # Aggregation option that collapses all results
    # TODO update logic if aggregation is used
    if aggregate:
        bin_incoherence_freq = 0
        for i, dict in enumerate(_bin):
            if dict['correct_response']:
                bin_incoherence_freq += 1
        print('Percent evaluated as incoherent: ' + str(bin_incoherence_freq / len(_bin) * 100))
    # Separates results based on the category selected. This is often going to be the sample's dataset
    else:
        while categories_list:
            to_check = categories_list.pop()
            # Temporary list containing the results in the correct category
            temp_list = []
            for i, dict in enumerate(_bin):
                if dict['Input.Dataset'] == to_check:
                    temp_list.append(dict)

            incoherence_agreement = count_incoherence_agreement(agreement_threshold, temp_list)
            bin_incoherence_freq = evaluate_incoherence_frequency(temp_list)
            result[to_check] = {'incoherence_agreement':incoherence_agreement, 'bin_incoherence_freq': bin_incoherence_freq, 'total_size': len(temp_list)}

        return result


def count_incoherence_agreement(agreement_threshold, temp_list, count_with_0_confidence = False):
    """
    First sorts the list to ensure that the same samples are placed next to eachother. After this is done, the
    frequency of correct answers are calculated over the total possible answers. A particular sample is counted when it
    meets the agreement threshold criteria
    :param agreement_threshold: decimal fraction required to count a particular question as correctly labelled incoherent
    :param temp_list:
    :param do_not_count_with_0_confidence: optional boolean that removes passing results if user answered followup with 0
    :return:
    """

    # Sorts the list so that questions for the same sample pairs will appear in sequence
    temp_list = sorted(temp_list, key=lambda k: (k['Input.Sample1'], k['Input.Sample2']))

    coherent_counter = 0
    incoherent_counter = 0
    score = 0
    possible_score = 0

    testing_sample = (temp_list[0]['Input.Sample1'], temp_list[0]['Input.Sample2'])

    for row in temp_list:
        if (row['Input.Sample1'], row['Input.Sample2']) == testing_sample:
            # Includes user's answer regardless of confidence level
            if count_with_0_confidence:
                if row['correct_answer']:
                    incoherent_counter += 1
                else:
                    coherent_counter += 1
            # Only includes user's answer if they do not have confidence 0 in their followup answer
            else:
                if row['correct_answer'] and row['Answer.FollowupAnswer'] != '0':
                    incoherent_counter += 1
                else:
                    coherent_counter += 1
        else:
            # Tally result
            if incoherent_counter/(incoherent_counter+coherent_counter) >= agreement_threshold:
                score += 1
            possible_score += 1

            # Reset parameters
            coherent_counter = 0
            incoherent_counter = 0

            # Set to next testing sample
            testing_sample = (row['Input.Sample1'], row['Input.Sample2'])
            if row['correct_answer']:
                incoherent_counter += 1
            else:
                coherent_counter += 1

    # For last sample
    if incoherent_counter / (incoherent_counter+coherent_counter) >= agreement_threshold:
        score += 1
    possible_score += 1

    return(score, possible_score)


def evaluate_incoherence_frequency(categories_list):
    """
    Counds the number of texts that were correctly labelled incoherent
    :param categories_list:
    :return:
    """

    bin_incoherence_freq = 0
    for i, dict in enumerate(categories_list):
        if dict['correct_answer']:
            bin_incoherence_freq += 1

    return bin_incoherence_freq

def remove_dataset(csv_data, dataset_to_remove):
    """
    Removes a dataset from the csv_data
    :param csv_data:
    :param dataset_to_remove: str containing the dataset name
    :return:
    """

    new_csv_data = []
    for item in csv_data:
        if item['dataset'] != dataset_to_remove:
            new_csv_data.append(item)
    return new_csv_data


def get_diff_values_from_category(csv_data, category):
    """
    Create a list of all possible values in a specific category
    :param csv_data:
    :param category:
    :return:
    """
    listed = []
    for item in csv_data:
        if item[category] not in listed:
            listed.append(item[category])
    return listed


def count_from_country(csv_data, countries_list):
    """
    Deprecated. Was used to count countries for CrowdFlower data. In Mechanical Turks Test only people in the US
    were tested
    :param csv_data:
    :param countries_list:
    :return:
    """

    english_country_counter = 0.0
    total_country_counter = 0.0

    for result in csv_data:
        if result['_country'] in countries_list:
            english_country_counter = english_country_counter + 1
        total_country_counter = total_country_counter + 1

    # print english_country_counter
    # print total_country_counter
    percent_country = english_country_counter/total_country_counter
    print('Country Percentage: ' + str(percent_country))


def remove_infrequent_samples(csv_data, sample_threshold):
    """
    Removes samples from the result data that do not have sufficient samples. This makes sense when they will not satisfy
    a certain sample_threshold which is the number of responses to a specific sample pair
    :param csv_data:
    :param sample_threshold: The minimum number of samples required for the result to be considered
    :return:
    """

    sorted_by_sample = sorted(csv_data, key=lambda k: k['sample'])

    counter = 0
    testing_sample = sorted_by_sample[0]['sample']
    marked_for_removal = []
    for dict in sorted_by_sample:
        # print dict['sample']
        if dict['sample'] == testing_sample:
            counter += 1
            # print(counter)
        else:
            if counter < sample_threshold:
                marked_for_removal.append(testing_sample)
            testing_sample = dict['sample']
            counter = 1
            # print(counter)
    # For last sample
    if counter < sample_threshold:
        marked_for_removal.append(testing_sample)

    new_dict_list = []
    for dict in csv_data:
        if dict['sample'] not in marked_for_removal:
            new_dict_list.append(dict['sample'])

    return new_dict_list

    # print(marked_for_removal)
    # print(len(marked_for_removal))

def update_correct_answers_old(csv_data):
    """
        Depricated: Adds a new key 'correct_answer' indicating whether the answer for each row was correct through a boolean
        :param csv_data:
        :return:
        """

    correct_counter = 0
    incorrect_counter = 0

    for line in csv_data:
        correct_answer = int(line['Input.Incoherent_Sample'].strip())
        answer_given = line['Answer.Answer'].strip()

        # TODO handle empty submission
        if (answer_given == '2'):
            correct_counter += 1
            line['correct_answer'] = True
        elif (answer_given == '1'):
            incorrect_counter += 1
            line['correct_answer'] = False
        else:
            print 'Empty response'
            line['correct_answer'] = False

    # print correct_counter
    # print incorrect_counter

    return csv_data

def update_correct_answers_new(csv_data):
    """
    Adds a new key 'correct_answer' indicating whether the answer for each row was correct through a boolean
    :param csv_data:
    :return:
    """

    correct_counter = 0
    incorrect_counter = 0

    for line in csv_data:
        correct_answer = int(line['Input.Incoherent_Sample'].strip())
        answer_given = line['Answer.Answer'].strip()
        print('Answer given: ')
        print(answer_given)
        print('Expected: ')
        print(line['Input.Incoherent_Sample'])

        print

        #TODO handle empty submission
        if (answer_given == '1' and correct_answer == 1) or (answer_given == '2' and correct_answer == 2):
            correct_counter += 1
            line['correct_answer'] = True
        elif (answer_given == '1' and correct_answer != 1) or (answer_given == '2' and correct_answer != 2):
            incorrect_counter += 1
            line['correct_answer'] = False
        else:
            print 'Empty response'
            line['correct_answer'] = False

    # print correct_counter
    # print incorrect_counter

    return csv_data


def get_results_with_agreement(csv_data, agreement_threshold, categories_list, bins = None, aggregate = False):
    """
    Gets the results based meeting the agreement threshold
    :param csv_data: All loaded data from the csv
    :param agreement_threshold: Fraction criteria that must be met for passing result
    :param categories_list: The different datasets the incoherent_sentences were initial drawn from
    :param bins: Pre-binned data from the csv_data. This can be used to group data by word length, for instance
    :param aggregate: Option aggregate results
    :return:
    """
    # Sets all csv_data to a single bin when it is not already set
    if not bins:
        bins = [csv_data]

    # Gets result lists from each bin
    result_list = []
    for _bin in bins:
        result_list.append(
            get_bin_data(_bin, list(categories_list), agreement_threshold, aggregate=aggregate))

    return result_list

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

def expand_csv_data(csv_data, length_of_questionnaire):
    """
    Adapter
    Transforms imported CSV data to the previous structure in order to simplify parsing and reuse existing functionality
    :return:
    """
    new_csv_data = []
    for row in csv_data:
        if not row['RejectionTime']:
            for i in range(1,length_of_questionnaire+1):
                new_csv_row = {'WorkerId': row['WorkerId'],
                               'CreationTime': row['CreationTime'],
                               'Input.Sample1': row['Input.Sample' + str(i) + '_' + str(1)],
                               'Input.Sample2': row['Input.Sample' + str(i) + '_' + str(2)],
                               'Input.Incoherent_Sample': row['Input.Incoherent_Sample' + str(i)],
                               'Answer.FollowupAnswer': row['Answer.FollowupAnswer' + str(i)],
                               'Answer.Answer': row['Answer.Answer' + str(i)],
                               'Input.Dataset': row['Input.Sample' + str(i) + 'Dataset'],
                               'AcceptTime': row['AcceptTime'],
                               'SubmitTime': row['SubmitTime'],
                               'RequesterFeedback': row['RequesterFeedback'],
                               'HITId': row['HITId']
                               }
                new_csv_data.append(new_csv_row)

    return new_csv_data


def set_time_elapsed(csv_data):
    """
    Gets the time delta between the AcceptTime and SubmitTime of a job
    :param csv_data:
    :return:
    """
    for row in csv_data:
        s1 = row['AcceptTime'].split()[3]
        s2 = row['SubmitTime'].split()[3]
        FMT = '%H:%M:%S'
        tdelta = datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)
        row['TimeElapsed'] = str(tdelta)

def count_instances_multiquestion_hit(csv_data, value):
    """
    Counts the number of occurrences of a given value
    :param csv_data:
    :param key:
    :return:
    """
    counter = 0
    for row in csv_data:
        for key in row:
            if row[key] == value:
                counter += 1
    print('Instances of ' + value + ': ' + str(counter))


def count_instances(csv_data, key):
    """
    Counts the number of occurrences of a value given a specified key
    :param csv_data:
    :param key:
    :return:
    """
    occurence_dict = {}
    for row in csv_data:
        if row[key] not in occurence_dict:
            occurence_dict[row[key]] = 1
        else:
            occurence_dict[row[key]] += 1
    print(occurence_dict)

def evaluate_single_user(original_csv_data, worker_id):
    """
    Removes all data except a particular user's
    :param worker_id:
    :return:
    """
    key = 'WorkerId'

    single_user_dict_list = []
    for row in original_csv_data:
        if row[key] == worker_id:
            single_user_dict_list.append(row)

    return single_user_dict_list



def remove_duplicate_submissions(original_csv_data):
    """
    Removes duplicate, keeping the latest form submission
    :param original_csv_data:
    :return:
    """
    # Add tuples containing the WorkerId and Input.Sample2_1
    worker_id_sentence_pair = set()

    # If adding the tuple to the set doesn't increase its size, there is a duplicate
    original_csv_data_no_dupes = []

    for row in reversed(original_csv_data):
        set_size = len(worker_id_sentence_pair)
        worker_id_sentence_pair.add((row['WorkerId'], row['Input.Sample2_1']))
        if set_size == len(worker_id_sentence_pair):
            continue
        original_csv_data_no_dupes.append(row)

    original_csv_data_no_dupes = [x for x in reversed(original_csv_data_no_dupes)]
    return original_csv_data_no_dupes

if __name__ == '__main__':

    original_csv_data = read_csv()
    original_csv_data = remove_duplicate_submissions(original_csv_data)
    count_instances(original_csv_data, 'WorkerId')
    # worker_id = 'justin.whatley@mail.mcgill.ca'
    # original_csv_data = evaluate_single_user(original_csv_data, worker_id)

    # Distributes CSV rows to columnsls

    # print(original_csv_data)
    length_of_questionnaire = get_number_of_questions(original_csv_data)
    if length_of_questionnaire > 1:
        csv_data = expand_csv_data(original_csv_data, length_of_questionnaire)
    else:
        csv_data = original_csv_data

    # set_time_elapsed(csv_data)
    count_instances(csv_data, 'Input.Dataset')

    #csv_data = include_only_this_dataset(csv_data, '.txt')

    print('The datasets included are: ')
    print(get_diff_values_from_category(csv_data, 'Input.Dataset'))

    # sample_threshold = 4
    # remove_infrequent_samples(csv_data, sample_threshold)

    agreement_threshold = 2/3
    update_correct_answers_new(csv_data)

    # for row in csv_data:
    #     print(row['TimeElapsed'],row['correct_answer'], row['WorkerId'], row['Answer.FollowupAnswer'], row['HITId'], row['Input.Incoherent_Sample'], row['Input.Sample1'], row['Input.Sample2'])

    #Gets the different corruption method datasets
    categories_list = get_diff_values_from_category(csv_data, 'Input.Dataset')
    result_list = get_results_with_agreement(csv_data, agreement_threshold, categories_list)
    print(cluster_matching_datasets(list(categories_list), result_list, agreement_threshold=agreement_threshold))

