#!/usr/bin/env python
from __future__ import division
import os.path as path
import glob
import csv

# Graph Imports
# import matplotlib.pyplot as plt
# import matplotlib.mlab as mlab
import numpy as np


crowdflower_output_directory = 'crowdflower_output_data'
mechanical_turks_output_directory = 'mechanical_turks_output_data'
batch = 'Batch_3108852_batch_results.csv'


def read_csv():
    directory = mechanical_turks_output_directory

    csv_list_of_dicts = []
    #TODO ensure that different header information does not break functionality down the line
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


def get_sentence_length_based_results(csv_data, agreement_threshold, length_type='word', aggregate = False):

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
    # Clusters matching dataset labels
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
    return ("Percent Incoherent: " + str(
                dict[to_check]['bin_incoherence_freq'] / dict[to_check]['total_size'] * 100)
               + '\n')

def output_percent_incoherence_with_annotator_agreement(dict, to_check, agreement_threshold):
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
    if aggregate:
        bin_incoherence_freq = 0
        for i, dict in enumerate(_bin):
            if dict['correct_response']:
                bin_incoherence_freq += 1

        print('Percent evaluated as incoherent: ' + str(bin_incoherence_freq / len(_bin) * 100))
    else:
        while categories_list:
            to_check = categories_list.pop()
            temp_list = []
            for i, dict in enumerate(_bin):
                if dict['Input.Dataset'] == to_check:
                    temp_list.append(dict)

            incoherence_agreement = count_incoherence_agreement(agreement_threshold, temp_list)
            bin_incoherence_freq = evaluate_incoherence_frequency(temp_list)
            result[to_check] = {'incoherence_agreement':incoherence_agreement, 'bin_incoherence_freq': bin_incoherence_freq, 'total_size': len(temp_list)}

        return result


def count_incoherence_agreement(agreement_threshold, temp_list):
    # for category to check
    # for every unique sample to check
    # ensure that the result is above the threshold (which will be a fraction)
    # return a fraction consisting of the samples meeting the threshold over the ones that did not


    coherent_counter = 0
    incoherent_counter = 0
    score = 0
    possible_score = 0

    testing_sample = (temp_list[0]['Input.Sample1'], temp_list[0]['Input.Sample2'])

    for dict in temp_list:
        if (dict['Input.Sample1'], dict['Input.Sample2']) == testing_sample:
            if dict['correct_answer']:
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
            testing_sample = (dict['Input.Sample1'], dict['Input.Sample2'])
            if dict['correct_answer']:
                incoherent_counter += 1
            else:
                coherent_counter += 1

    # For last sample
    if incoherent_counter / (incoherent_counter+coherent_counter) >= agreement_threshold:
        score += 1
    possible_score += 1

    return(score, possible_score)


def evaluate_incoherence_frequency(categories_list):

    bin_incoherence_freq = 0
    for i, dict in enumerate(categories_list):
        if dict['correct_answer']:
            bin_incoherence_freq += 1

    return bin_incoherence_freq

def remove_dataset(csv_data, dataset_to_remove):
    new_csv_data = []
    for item in csv_data:
        if item['dataset'] != dataset_to_remove:
            new_csv_data.append(item)
    return new_csv_data


def get_diff_values_from_category(csv_data, category):
    listed = []
    for item in csv_data:
        if item[category] not in listed:
            listed.append(item[category])
    return listed


def count_from_country(csv_data, countries_list):

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
    Removes samples from the result data that do not have sufficient samples
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

def update_correct_answers(csv_data):
    """
    Adds
    :param csv_data:
    :return:
    """

    correct_counter = 0
    incorrect_counter = 0
    for line in csv_data:
        correct_answer = int(line['Input.Incoherent_Sample'].strip())
        answer_given = line['Answer.Answer'].strip()
        # print line['WorkerId']
        # print correct_answer
        # print answer_given

        #TODO handle empty submission
        if (answer_given == 'SampleText1' and correct_answer == 1) or (answer_given == 'SampleText2' and correct_answer == 2):
            correct_counter += 1
            line['correct_answer'] = True
        elif (answer_given == 'SampleText1' and correct_answer != 1) or (answer_given == 'SampleText2' and correct_answer != 2):
            incorrect_counter += 1
            line['correct_answer'] = False
        else:
            print 'Empty response'
            line['correct_answer'] = False

    # print correct_counter
    # print incorrect_counter

    return csv_data


def get_results_with_agreement(csv_data, agreement_threshold, categories_list, bins = None, aggregate = False):
    if not bins:
        bins = [csv_data]
    result_list = []
    for _bin in bins:
        result_list.append(
            get_bin_data(_bin, list(categories_list), agreement_threshold, aggregate=aggregate))
    return result_list


if __name__ == '__main__':

    csv_data = read_csv()
    # csv_data = remove_dataset(csv_data, 'incoherent_sentences_randomized_words.txt')

    #csv_data = include_only_this_dataset(csv_data, '.txt')

    print('The datasets included are: ')
    print(get_diff_values_from_category(csv_data, 'Input.Dataset'))

    # sample_threshold = 4
    # remove_infrequent_samples(csv_data, sample_threshold)

    agreement_threshold =3 / 4
    update_correct_answers(csv_data)

    #Gets the different corruption method datasets
    categories_list = get_diff_values_from_category(csv_data, 'Input.Dataset')
    result_list = get_results_with_agreement(csv_data, agreement_threshold, categories_list)
    print(cluster_matching_datasets(list(categories_list), result_list, agreement_threshold=agreement_threshold))


    # get_sentence_length_based_results(csv_data, agreement_threshold)

    # for item in csv_data:
    #     print(item)

