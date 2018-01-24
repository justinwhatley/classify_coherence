#!/usr/bin/env python
from __future__ import division
import os.path as path
import glob
import csv

# Graph Imports
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import numpy as np


crowdflower_output_directory = 'crowdflower_output_data'


def read_csv():

    csv_list_of_dicts = []
    #TODO ensure that different header information does not break functionality down the line
    for filename in glob.glob(path.join(crowdflower_output_directory, '*.csv')):
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
        result_list.append(get_bin_data(_bin, list(categories_list), agreement_threshold=agreement_threshold, aggregate=aggregate))

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
    return ('Range: [' + str(dict['range'][0]) + ":" + str(dict['range'][1]) + ']'
               + "  Percent Incoherent: " + str(
                dict[to_check]['bin_incoherence_freq'] / dict[to_check]['total_size'] * 100)
               + '\n')

def output_percent_incoherence_with_annotator_agreement(dict, to_check, agreement_threshold):
    return ('Range: [' + str(dict['range'][0]) + ":" + str(dict['range'][1]) + ']'
            + "  Percent Incoherent at " + str(agreement_threshold) + " agreement: " +  str(
                dict[to_check]['incoherence_agreement'][0] / dict[to_check]['incoherence_agreement'][1] * 100)
            + " (" + str(dict[to_check]['incoherence_agreement'][0]) + " labelled incoherent at agreement rate out of "
            + str(dict[to_check]['incoherence_agreement'][1]) + " possible)"
            + '\n')
# Before evaluate coherence with threshold
# def get_bin_data(_bin, categories_list, agreement_threshold, aggregate=False):
#     """
#     Prints text length ranges as well as the percent of responses that were evaluated as incoherent
#     :param _bin:
#     :return:
#     """
#     result = {}
#     lower_boundary = _bin[0]['sample_length']
#     upper_boundary = _bin[-1]['sample_length']
#     result['range'] = (lower_boundary, upper_boundary)
#
#     # print('\nRange: [' + str(lower_boundary) + ' : ' + str(upper_boundary) + ']')
#     if aggregate:
#         bin_incoherence_freq = 0
#         for i, dict in enumerate(_bin):
#
#
#             if is_incoherent(dict):
#                 bin_incoherence_freq += 1
#
#         print('Percent evaluated as incoherent: ' + str(bin_incoherence_freq / len(_bin) * 100))
#
#     else:
#         while categories_list:
#             to_check = categories_list.pop()
#             temp_list = []
#             for i, dict in enumerate(_bin):
#                 if dict['dataset'] == to_check:
#                     temp_list.append(dict)
#
#             bin_incoherence_freq = 0
#             for i, dict in enumerate(temp_list):
#                 if is_incoherent(dict):
#                     bin_incoherence_freq += 1
#
#             result[to_check] = {'bin_incoherence_freq': bin_incoherence_freq, 'total_size': len(temp_list)}
#
#         return result
#             # print('Percent evaluated as incoherent: ' + str(bin_incoherence_freq/len(temp_list)*100))


def get_bin_data(_bin, categories_list, agreement_threshold, aggregate=False):
    """
    Prints text length ranges as well as the percent of responses that were evaluated as incoherent
    :param _bin:
    :return:
    """
    result = {}
    lower_boundary = _bin[0]['sample_length']
    upper_boundary = _bin[-1]['sample_length']
    result['range'] = (lower_boundary, upper_boundary)

    # print('\nRange: [' + str(lower_boundary) + ' : ' + str(upper_boundary) + ']')
    if aggregate:
        bin_incoherence_freq = 0
        for i, dict in enumerate(_bin):


            if is_incoherent(dict):
                bin_incoherence_freq += 1

        print('Percent evaluated as incoherent: ' + str(bin_incoherence_freq / len(_bin) * 100))

    else:
        while categories_list:
            to_check = categories_list.pop()
            temp_list = []
            for i, dict in enumerate(_bin):
                if dict['dataset'] == to_check:
                    temp_list.append(dict)

            incoherence_agreement = evaluate_incoherence_agreement(agreement_threshold, temp_list)
            bin_incoherence_freq = evaluate_incoherence_frequency(temp_list)
            result[to_check] = {'incoherence_agreement':incoherence_agreement, 'bin_incoherence_freq': bin_incoherence_freq, 'total_size': len(temp_list)}

        return result
            # print('Percent evaluated as incoherent: ' + str(bin_incoherence_freq/len(temp_list)*100))


def evaluate_incoherence_agreement(agreement_threshold, temp_list):
    # for category to check
    # for every unique sample to check
    # ensure that the result is above the threshold (which will be a fraction)
    # return a fraction consisting of the samples meeting the threshold over the ones that did not

    coherent_counter = 0
    incoherent_counter = 0
    score = 0
    possible_score = 0

    testing_sample = temp_list[0]['sample']
    for dict in temp_list:
        if dict['sample'] == testing_sample:
            if is_incoherent(dict):
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
            testing_sample = dict['sample']
            if is_incoherent(dict):
                incoherent_counter += 1
            else:
                coherent_counter += 1

    # For last sample
    if incoherent_counter / coherent_counter >= agreement_threshold:
        score += 1
    possible_score += 1
    #
    # print('Score: ' + str(score))
    # print('Possible score: ' + str(possible_score))

    return(score, possible_score)


def evaluate_incoherence_frequency(categories_list):

    bin_incoherence_freq = 0
    for i, dict in enumerate(categories_list):
        if is_incoherent(dict):
            bin_incoherence_freq += 1

    return bin_incoherence_freq

def is_incoherent(dict):
    if dict['please_classify_the_sample'] == 'incoherent':
        return True
    return False

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


# def make_bar_chart(bins):
#
#     N = len(bins)
#
#     men_means = (20, 35, 30, 35, 27)
#     men_std = (2, 3, 4, 1, 2)
#
#     ind = np.arange(N)  # the x locations for the groups
#     width = 0.35       # the width of the bars
#
#     fig, ax = plt.subplots()
#     rects1 = ax.bar(ind, men_means, width, color='r', yerr=men_std)
#
#     women_means = (25, 32, 34, 20, 25)
#     women_std = (3, 5, 2, 3, 3)
#     rects2 = ax.bar(ind + width, women_means, width, color='y', yerr=women_std)
#
#     # add some text for labels, title and axes ticks
#     ax.set_ylabel('Scores')
#     ax.set_title('Scores by group and gender')
#     ax.set_xticks(ind + width / 2)
#     ax.set_xticklabels(('G1', 'G2', 'G3', 'G4', 'G5'))
#
#     ax.legend((rects1[0], rects2[0]), ('Men', 'Women'))
#
#     def autolabel(rects):
#         """
#     Attach a text label above each bar displaying its height
#     """
#         for rect in rects:
#             height = rect.get_height()
#             ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
#                     '%d' % int(height),
#                     ha='center', va='bottom')
#
#     autolabel(rects1)
#     autolabel(rects2)
#
#     plt.show()

# def make_histogram():
#     mu, sigma = 100, 15
#     x = mu + sigma * np.random.randn(10000)
#
#     # the histogram of the data
#     n, bins, patches = plt.hist(x, 50, normed=1, facecolor='green', alpha=0.75)
#
#     # add a 'best fit' line
#     y = mlab.normpdf(bins, mu, sigma)
#     l = plt.plot(bins, y, 'r--', linewidth=1)
#
#     plt.xlabel('Smarts')
#     plt.ylabel('Probability')
#     plt.title(r'$\mathrm{Histogram\ of\ IQ:}\ \mu=100,\ \sigma=15$')
#     plt.axis([40, 160, 0, 0.03])
#     plt.grid(True)
#
#     plt.show()


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



if __name__ == '__main__':

    csv_data = read_csv()
    csv_data = remove_dataset(csv_data, 'incoherent_sentences_randomized_words.txt')

    #csv_data = include_only_this_dataset(csv_data, '.txt')

    print('The datasets included are: ')
    print(get_diff_values_from_category(csv_data, 'dataset'))

    sample_threshold = 4
    remove_infrequent_samples(csv_data, sample_threshold)

    agreement_threshold = 3 / 4
    get_sentence_length_based_results(csv_data, agreement_threshold)

    # countries_list = ['GBR', 'CAN', 'USA', 'JAM', 'IDN']
    # # countries_list = ['VEN']
    # print(count_from_country(csv_data, countries_list))

    # for item in csv_data:
    #     print(item)

