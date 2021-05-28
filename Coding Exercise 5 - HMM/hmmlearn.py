import sys
import os
import string


def get_data(inputfile):
    sentences = []
    with open(inputfile, 'r') as f:
        txt = f.readline()
        while txt:
            sentences.append(txt.split())
            txt = f.readline()
    return sentences


def get_probabilities(sentences):
    transitions, emissions = {}, {}
    transition_counts, emission_counts = {}, {}
    start = "Initial"
    end = "Finish"
    prev_tag = "None"
    transition_counts[start] = len(sentences) 
    transitions[start] = {}

    for sentence in sentences:
        for i in range(len(sentence)):
            index = sentence[i].rfind('/')
            word = sentence[i][:index].lower()
            tag = sentence[i][index + 1:]
            # Keep track of total tag emissions
            if tag in emission_counts:
                emission_counts[tag] += 1
            else:
                emission_counts[tag] = 1
            # Keep track of word - tag emissions
            if word in emissions:
                if tag in emissions[word]:
                    emissions[word][tag] += 1
                else:
                    emissions[word][tag] = 1
            else:
                emissions[word] = {}
                emissions[word][tag] = 1

            # Keep track of transitions
            if i == 0:
                if tag in transitions[start]:
                    transitions[start][tag] += 1
                else:
                    transitions[start][tag] = 1
                prev_tag = tag
            else:
                if prev_tag in transitions:
                    if tag in transitions[prev_tag]:
                        transitions[prev_tag][tag] += 1
                    else:
                        transitions[prev_tag][tag] = 1
                    transition_counts[prev_tag] += 1
                else:
                    transitions[prev_tag] = {}
                    transitions[prev_tag][tag] = 1
                    transition_counts[prev_tag] = 1
                prev_tag = tag 
            if i == (len(sentence) - 1):
                if tag in transitions:
                    if end in transitions[tag]:
                        transitions[tag][end] += 1
                    else:
                        transitions[tag][end] = 1
                    transition_counts[tag] += 1
                else:
                    transitions[tag] = {}
                    transitions[tag][end] = 1  
                    transition_counts[tag] = 1   

    ecount = 0
    for word in emissions:
        for tag in emissions[word]:
            emissions[word][tag] = float(emissions[word][tag] / emission_counts[tag])
            ecount += 1

    tcount = 0
    t_types = []
    for tag_from in transitions:
        temp = 0
        for tag_to in transitions[tag_from]:
            if tag_to not in t_types:
                t_types.append(tag_to)
            temp += transitions[tag_from][tag_to]
            tcount += 1
        transitions[tag_from]["Total"] = temp
        tcount += 1

    return transitions, emissions, ecount, tcount, t_types

def create_model(transitions, emissions, ecount, tcount, num_types):
    with open('hmmmodel.txt', 'w') as f:
        f.write("Emission probabilities - word, TAG, float - #{0}\n".format(ecount))
        for word in emissions:
            for tag in emissions[word]:
                f.write("{0} {1} {2}\n".format(word, tag, emissions[word][tag]))
        f.write("Transition probabilities - TAG1, TAG2, float - #{0}\n".format(tcount))
        f.write("Transition types - #{0}\n".format(num_types))
        for tag_from in transitions:
            for tag_to in transitions[tag_from]:
                f.write("{0} {1} {2}\n".format(tag_from, tag_to, transitions[tag_from][tag_to]))


def main(argv):
    sentences = get_data(argv[0])
    transitions, emissions, ecount, tcount, transition_types = get_probabilities(sentences)
    create_model(transitions, emissions, ecount, tcount, len(transition_types))

if __name__ == "__main__":
    main(sys.argv[1:])
