import sys
import os
import string


def read_model():
    transitions, emissions = {}, {}
    with open('hmmmodel.txt', 'r') as f:
        lines = f.readlines()
    index = int(lines[0][lines[0].find('#') + 1:])
    emission_lines = lines[1:index + 1]
    transition_types = int(lines[index + 2][lines[index + 2].find('#') + 1:])
    transition_lines = lines[index + 3:]

    # Populate emissions dictionary
    for line in emission_lines:
        values = line.split()
        word, tag, prob = [values[i] for i in (0,1,2)]
        if word in emissions:
            emissions[word][tag] = float(prob) 
        else:
            emissions[word] = {}
            emissions[word][tag] = float(prob)
    
    # Populate transitions dictionary
    for line in transition_lines:
        values = line.split()
        tag1, tag2, prob = [values[i] for i in (0,1,2)]
        if tag1 in transitions:
            transitions[tag1][tag2] = float(prob)
        else:
            transitions[tag1] = {}
            transitions[tag1][tag2] = float(prob)

    return transitions, emissions, transition_types


def get_testdata(inputfile):
    test_data, original_data = [], []
    with open(inputfile, 'r') as f:
        line = f.readline()
        while line:
            words = line.split()
            original_data.append(words)
            words = [word.lower() for word in words]
            test_data.append(words)
            line = f.readline()

    return test_data, original_data


def classify(transitions, emissions, transition_types, test_data):
    test_tags = []
    # Viterbi algorithm
    start, end = 'Initial', 'Finish'

    for sentence in test_data:
        backpointers = []
        for i in range(len(sentence)):
            backpointers.append({})
            word = sentence[i]
            if word in emissions:
                if i == 0:
                    # 1 to M 
                    for tag in emissions[word]:
                        if tag != end and tag != 'Total':
                            if tag in transitions[start]:
                                backpointers[i][tag] = [(transitions[start][tag] + 1) / (transition_types + transitions[start]['Total']) * emissions[word][tag], start]
                            else:
                                backpointers[i][tag] = [1 / (transition_types + transitions[start]['Total']) * emissions[word][tag], start]
                else:
                    # M to M
                    for prev_tag in backpointers[i - 1]:
                        for tag in emissions[word]:
                            if tag != end and tag != 'Total':
                                if tag in transitions[prev_tag]:
                                    if tag in backpointers[i]:
                                        prob = backpointers[i - 1][prev_tag][0] * (transitions[prev_tag][tag] + 1) / (transition_types + transitions[prev_tag]['Total']) * emissions[word][tag]
                                        if prob > backpointers[i][tag][0]:
                                            backpointers[i][tag] = [prob, prev_tag]
                                    else:
                                        backpointers[i][tag] = [backpointers[i - 1][prev_tag][0] * (transitions[prev_tag][tag] + 1) / (transition_types + transitions[prev_tag]['Total']) * emissions[word][tag], prev_tag]
                                else:
                                    prob = backpointers[i - 1][prev_tag][0] / (transition_types + transitions[prev_tag]['Total']) * emissions[word][tag]
                                    if tag in backpointers[i]:
                                        if prob > backpointers[i][tag][0]:
                                            backpointers[i][tag] = [prob, prev_tag]
                                    else:
                                        backpointers[i][tag] = [backpointers[i - 1][prev_tag][0] / (transition_types + transitions[prev_tag]['Total']) * emissions[word][tag], prev_tag]
            else:
                if i == 0:
                    for tag in transitions[start]:
                        if tag != end and tag != 'Total':
                            backpointers[i][tag] = [(transitions[start][tag] + 1) / (transition_types + transitions[start]['Total']), start]
                else:
                    for prev_tag in backpointers[i - 1]:
                        for tag in transitions[prev_tag]:
                            if tag != end and tag != 'Total':
                                if tag in backpointers[i]:
                                    prob = backpointers[i - 1][prev_tag][0] * (transitions[prev_tag][tag] + 1) / (transition_types + transitions[prev_tag]['Total'])
                                    if prob > backpointers[i][tag][0]:
                                        backpointers[i][tag] = [prob, prev_tag]
                                else:
                                    backpointers[i][tag] = [backpointers[i - 1][prev_tag][0] * (transitions[prev_tag][tag] + 1) / (transition_types + transitions[prev_tag]['Total']), prev_tag]
                                    
            if i == (len(sentence) - 1):    
                # M to 1
                backpointers.append({})
                biggest = [0, 'NoTag']
                for tag in backpointers[i]:
                    if end in transitions[tag]:
                        prob = backpointers[i][tag][0] * (transitions[tag][end] + 1) / (transition_types + transitions[tag]['Total'])
                        if prob > biggest[0]:
                            biggest = [prob, tag]
                    else:
                        prob = backpointers[i][tag][0] / (transition_types + transitions[tag]['Total'])
                        if prob > biggest[0]:
                            biggest = [prob, tag]
                backpointers[i+1][end] = biggest

        # Add sequence to output
        sentence_tags = []
        sentence_tags.append(backpointers[len(backpointers)-1][end][1])
        for i in reversed(range(len(backpointers) - 1)):
            if i > 0:
                sentence_tags.insert(0, backpointers[i][sentence_tags[0]][1])
        test_tags.append(sentence_tags)

    return test_tags


def create_output(original_data, test_tags):
    with open('hmmoutput.txt', 'w') as f:
        for i in range(len(original_data)):
            for j in range(len(original_data[i])):
                if j == len(original_data[i]) - 1:
                    f.write("{0}/{1}\n".format(original_data[i][j], test_tags[i][j]))
                else:
                    f.write("{0}/{1} ".format(original_data[i][j], test_tags[i][j]))


def main(argv):
    transitions, emissions, transition_types = read_model()
    test_data, original_data = get_testdata(argv[0])
    test_tags = classify(transitions, emissions, transition_types, test_data)
    create_output(original_data, test_tags)

if __name__ == "__main__":
    main(sys.argv[1:])