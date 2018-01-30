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
    sentence = {
        'Arg1Raw': arg1,
        'Arg2Raw': arg2,
        'ConnectiveRaw': connective.lower(),
        'Sense': sense.lower(),
    }
    return sentence

def create_sentence_pair(arg1, arg2, connective, sense, original_sentence_index):
    sentence = {
        'Arg1Raw': arg1,
        'Arg2Raw': arg2,
        'ConnectiveRaw': connective.lower(),
        'Sense': sense.lower(),
        'Original_Sentence_Index': original_sentence_index
    }
    return sentence


def keep_only_top_level_sense():
    # Only keep top level Sense
    for line in data:
        top_level_sense = ""
        for sense in line['Sense']:
            split_sense = sense.split('.', 1)
            top_level_sense = split_sense[0]
        line['Sense'] = top_level_sense

def remove_sentences_with_explicit_connectives():
    # Remove sentence with Explicit connectives
    global data
    data = (filter(lambda line: line['Type'] != 'Explicit', data))

def include_only_sentences_of_type(type):
    global data
    data = (filter(lambda line: line['Type'] == type, data))

def display_different_types():
    global data


    type = []
    for line in data:
        if line['Type'] not in type:
            type.append(line['Type'])

    print('Different types of sentences are: ')
    print(type)

def display_different_keys():
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
    for line in data:
        # Get a random sentence
        index = randint(0, len(coherent_copy) - 1)
        random_coherent_sentence = coherent_copy[index]

        coherent_copy.pop(index)  # Remove sentence with used Arg2 from set of sentences

        incoherent_sentences.append(create_sentence_pair(line['Arg1']['RawText'],
                                                    random_coherent_sentence['Arg2Raw'],
                                                    line['Connective']['RawText'],
                                                    line['Sense'],
                                                    index))
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
        tries = 0
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
    for line in data:
        # Get a random sentence that is not the same as the current one
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
        tries = 0
        coherent_copy.pop(index)  # Remove sentence with used Arg2 from set of sentences
        incoherent_sentences.append(create_sentence(line['Arg1']['RawText'],
                                                    random_coherent_sentence['Arg2Raw'],
                                                    line['Connective']['RawText'],
                                                    line['Sense']))
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

    # remove_sentences_with_explicit_connectives()
    include_only_sentences_of_type('Implicit')
    remove_sentences_with_unlisted_connectives()

    coherent_sentences = prepare_coherent_sentences()

    unique_connectives_senses = create_unique_connectives()

    generate_sentences_random_arg2(coherent_sentences)
    # generate_sentences_swapping_connectives(unique_connectives_senses)
    # generate_sentences_swapping_arg2_same_sense(unique_connectives_senses, coherent_sentences)
    # generate_sentences_swapping_arg2_different_sense(unique_connectives_senses, coherent_sentences)
    # generate_sentences_swapping_arg2_matching_connective(coherent_sentences)
    # generate_sentences_swapping_arg2_different_sense_connective(unique_connectives_senses)




