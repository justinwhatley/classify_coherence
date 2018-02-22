import json
from random import randint, sample

# Global variables
data = []          
connectives = []    

# Input
relations_json =                                   'data/relations-01-12-16-train.json'
# Output files 
coherent_sentences_file =                          'data/json/coherent_sentences.json'
incoherent_sentences_arg2_random =                 'data/json/incoherent_sentences_arg2_random.json'
incoherent_sentences_connective_random =           'data/json/incoherent_sentences_connective_random.json'
incoherent_sentences_arg2_same_sense =             'data/json/incoherent_sentences_arg2_same_sense.json'
incoherent_sentences_arg2_diff_sense =             'data/json/incoherent_sentences_arg2_diff_sense.json'
incoherent_sentences_arg2_matching_connectives =   'data/json/incoherent_sentences_arg2_matching_connectives.json'
incoherent_sentences_connective_diff_sense =       'data/json/incoherent_sentences_connective_diff_sense.json'

# Helper methods 
def output_sentences(sentences, output_file):
    open(output_file, 'w') # Clear contents of file 
    # Write sentences to output files 
    with open(output_file, 'a+') as out:
        for sentence in sentences:
            json.dump(sentence, out)
            out.write('\n')

def create_sentence(arg1, arg2, connective, sense):
    """
    Creates a sentence dictionary
    :param arg1:
    :param arg2:
    :param connective:
    :param sense:
    :return:
    """
    sentence = {
        'Arg1Raw': arg1,
        'Arg2Raw': arg2,
        'ConnectiveRaw': connective.lower(),
        'Sense': sense.lower(),
    }
    return sentence

def create_sentence_pair(arg1, arg2, connective, sense, original_sentence_index):
    """
    Creates a sentence dictionary which includes a reference to the original text before corruption
    :param arg1:
    :param arg2:
    :param connective:
    :param sense:
    :param original_sentence_index:
    :return:
    """
    sentence = {
        'Arg1Raw': arg1,
        'Arg2Raw': arg2,
        'ConnectiveRaw': connective.lower(),
        'Sense': sense.lower(),
        'OriginalSentenceIndex': original_sentence_index
    }
    return sentence


def keep_only_top_level_sense():
    """
    Removes all lower level sense in the data. Thus, leaving only the Comparison, Contingency, etc
    :return:
    """
    for line in data:
        top_level_sense = ""
        for sense in line['Sense']:
            split_sense = sense.split('.', 1)
            top_level_sense = split_sense[0]
        line['Sense'] = top_level_sense

def remove_sentences_with_explicit_connectives():
    """
    Removes sentences with explicit connectives from the data
    """
    global data
    data = (filter(lambda line: line['Type'] != 'Explicit', data))

def include_only_sentences_of_type(type):
    """
    Specify a specific type (i.e., 'Implicit') that will be used to
    :param type: str indicating the type
    :return:
    """
    global data
    data = (filter(lambda line: line['Type'] == type, data))

def display_different_types():
    """
    Outputs the different types of sentences contained in the data
    :return:
    """
    global data
    type = []
    for line in data:
        if line['Type'] not in type:
            type.append(line['Type'])

    print('Different types of sentences are: ')
    print(type)

def display_different_keys():
    """
    Show the different keys in a particular dictionary object
    :return: none
    """
    global data
    for dict in data:
        for line in dict.keys():
            print(line)
        break


def remove_sentences_with_unlisted_connectives():
    # Remove sentences with "" as Connective
    global data
    data = filter(lambda line: line['Connective']['RawText'] != '', data)
    data = filter(lambda line: line['Connective']['RawText'] != "", data)

def remove_texts_with_args_starting_midsentence():
    # Remove sentences that are separated by implicit connective mid-sentence
    global data
    data = filter(lambda line: line['Arg1']['RawText'][0].isupper(), data)
    data = filter(lambda line: line['Arg2']['RawText'][0].isupper(), data)

def remove_texts_with_nested_sentences():
    global data
    # Removes sentences containing a period to simplify dataset since these may be multipart arguments
    data = filter(lambda line: line['Arg1']['RawText'].rfind('.') == -1, data)
    data = filter(lambda line: line['Arg2']['RawText'].rfind('.') == -1, data)

def prepare_coherent_sentences():
    # Coherent sentences
    global data
    coherent_sentences = []
    for line in data:
        coherent_sentences.append(create_sentence(line['Arg1']['RawText'],
                                                  line['Arg2']['RawText'],
                                                  line['Connective']['RawText'],
                                                  line['Sense']))
        # Store 'arg2s' and 'connectives' to create incoherent sentences afterwards
        connective = {line['Connective']['RawText']: line['Sense']}
        connectives.append(connective)
    output_sentences(coherent_sentences, coherent_sentences_file)
    return coherent_sentences

def create_unique_connectives():
    # Create a set of unique connectives and their senses
    unique_connectives_senses = {}
    for i in iter(connectives):
        for c, s in i.items():
            if c not in unique_connectives_senses:
                unique_connectives_senses[c] = [s]
            elif s not in unique_connectives_senses[c]:
                unique_connectives_senses[c].append(s)

    return unique_connectives_senses

def generate_sentences_random_arg2(coherent_sentences):
    # RANDOM: Incoherent sentences by swapping Arg2s
    incoherent_sentences = []
    coherent_copy = list(coherent_sentences)
    for i, line in enumerate(data):
        # Get a random sentence
        index = randint(0, len(coherent_copy) - 1)
        random_coherent_sentence = coherent_copy[index]

        coherent_copy.pop(index)  # Remove sentence with used Arg2 from set of sentences

        incoherent_sentences.append(create_sentence_pair(line['Arg1']['RawText'],
                                                    random_coherent_sentence['Arg2Raw'],
                                                    line['Connective']['RawText'],
                                                    line['Sense'],
                                                    i))
    output_sentences(incoherent_sentences, incoherent_sentences_arg2_random)


def generate_sentences_swapping_connectives(unique_connectives_senses):
    # RANDOM: Incoherent sentences by swapping connectives
    incoherent_sentences = []
    for line in data:
        # Get a random connective
        connective_list = sample(unique_connectives_senses, 1)
        connective = connective_list[0]
        incoherent_sentences.append(create_sentence(line['Arg1']['RawText'],
                                                    line['Arg2']['RawText'],
                                                    connective,
                                                    next(iter(unique_connectives_senses[
                                                                  connective]))))  # Issue: this will always be the first element (thus the first possible Sense)
    output_sentences(incoherent_sentences, incoherent_sentences_connective_random)

def generate_sentences_swapping_arg2_same_sense(unique_connectives_senses, coherent_sentences):
    # SAME SENSE: Incoherent sentences by swapping Arg2s
    incoherent_sentences = []
    coherent_copy = list(coherent_sentences)
    for line in data:
        # Get a random sentence
        index = randint(0, len(coherent_copy) - 1)
        random_coherent_sentence = coherent_copy[index]

        # Ensure that connection between Arg1 and new Arg2 is the same as connection between Arg1 and original Arg2
        # Because this may not be possible for all sentences, we will try a maximum of 1000 times.
        tries = 0
        while (random_coherent_sentence['Sense'] not in unique_connectives_senses[
            line['Connective']['RawText']] and tries < 1000):
            index = randint(0, len(coherent_copy) - 1)
            random_coherent_sentence = coherent_copy[index]
            tries += 1
        coherent_copy.pop(index)  # Remove sentence with used Arg2 from set of sentences
        incoherent_sentences.append(create_sentence(line['Arg1']['RawText'],
                                                    random_coherent_sentence['Arg2Raw'],
                                                    line['Connective']['RawText'],
                                                    line['Sense']))
    output_sentences(incoherent_sentences, incoherent_sentences_arg2_same_sense)

def generate_sentences_swapping_arg2_different_sense(unique_connectives_senses, coherent_sentences):
    # DIFFERENT SENSE: Incoherent sentences by swapping Arg2s

    incoherent_sentences = []
    coherent_copy = list(coherent_sentences)
    for i, line in enumerate(data):
        # Get a random sentence that is not the same as the current one
        if line['Sense'] == 'Comparison' or line['Sense'] == 'Contingency':
            index = randint(0, len(coherent_copy) - 1)
            random_coherent_sentence = coherent_copy[index]

            # Ensure that connection between Arg1 and new Arg2 is not the same as connection between Arg1 and original Arg2
            # Because this may not be possible for all sentences, we will try a maximum of 1000 times.
            tries = 0
            while (random_coherent_sentence['Sense'] in unique_connectives_senses[
                line['Connective']['RawText']] and tries < 1000):
                index = randint(0, len(coherent_copy) - 1)
                random_coherent_sentence = coherent_copy[index]
                tries += 1
            coherent_copy.pop(index)  # Remove sentence with used Arg2 from set of sentences
            incoherent_sentences.append(create_sentence_pair(line['Arg1']['RawText'],
                                                        random_coherent_sentence['Arg2Raw'],
                                                        line['Connective']['RawText'],
                                                        line['Sense'],
                                                        i))
    output_sentences(incoherent_sentences, incoherent_sentences_arg2_diff_sense)

def generate_sentences_swapping_arg2_matching_connective(coherent_sentences):
    # MATCHING CONNECTIVE: Incoherent sentences by swapping Arg2s
    incoherent_sentences = []
    coherent_copy = list(coherent_sentences)
    for line in data:
        # Get a random sentence that is not the same as the current one
        index = randint(0, len(coherent_copy) - 1)
        random_coherent_sentence = coherent_copy[index]

        # Ensure that connection between Arg1 and new Arg2 is the same as connection between Arg1 and original Arg2
        # Because this may not be possible for all sentences, we will try a maximum of 1000 times.
        tries = 0
        while (random_coherent_sentence['ConnectiveRaw'] != line['Connective']['RawText'] and tries < 1000):
            index = randint(0, len(coherent_copy) - 1)
            random_coherent_sentence = coherent_copy[index]
            tries += 1
        if tries == 1000:
            continue
        tries = 0

        coherent_copy.pop(index)  # Remove sentence with used Arg2 from set of sentences
        incoherent_sentences.append(create_sentence(line['Arg1']['RawText'],
                                                    random_coherent_sentence['Arg2Raw'],
                                                    line['Connective']['RawText'],
                                                    line['Sense']))
    output_sentences(incoherent_sentences, incoherent_sentences_arg2_matching_connectives)

def extract_text_with_sense(sense):
    global data
    return filter(lambda line: line['Sense'] == sense, data)

def generate_sentences_swapping_arg2_different_sense_connective(unique_connectives_senses):
    # DIFFERENT SENSE CONNECTIVE: Incoherent sentences by swapping connectives
    incoherent_sentences = []

    for line in data:
        # Get a random connective
        connective_list = sample(unique_connectives_senses, 1)
        connective = connective_list[0]

        # Ensure connective does not have the same sense as the original
        while (line['Sense'] in unique_connectives_senses[connective]):
            connective_sample = sample(unique_connectives_senses, 1)
            connective = connective_sample[0]
        incoherent_sentences.append(create_sentence(line['Arg1']['RawText'],
                                                    line['Arg2']['RawText'],
                                                    connective,
                                                    next(iter(unique_connectives_senses[connective]))))
    output_sentences(incoherent_sentences, incoherent_sentences_connective_diff_sense)

if __name__ == '__main__':
    # Import relations data as a JSON object
    for line in open(relations_json, 'r'):
        data.append(json.loads(line))

    keep_only_top_level_sense()

    exlusive_connective_type = 'Implicit'
    include_only_sentences_of_type(exlusive_connective_type)

    if exlusive_connective_type == 'Implicit':
        remove_texts_with_nested_sentences()
        remove_texts_with_args_starting_midsentence()
        remove_sentences_with_unlisted_connectives()

        coherent_sentences = prepare_coherent_sentences()
        unique_connectives_senses = create_unique_connectives()

        # Generate sentences
        generate_sentences_random_arg2(coherent_sentences)
        # generate_sentences_swapping_connectives(unique_connectives_senses)
        # generate_sentences_swapping_arg2_same_sense(unique_connectives_senses, coherent_sentences)
        generate_sentences_swapping_arg2_different_sense(unique_connectives_senses, coherent_sentences)
        # generate_sentences_swapping_arg2_matching_connective(coherent_sentences)
        # generate_sentences_swapping_arg2_different_sense_connective(unique_connectives_senses)


    elif exlusive_connective_type == 'Explicit':
        coherent_sentences = prepare_coherent_sentences()




