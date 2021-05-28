import sys
import os
import string
import math


def find_folders(path):
    return [(path + "/" + folder) for folder in os.listdir(path) if os.path.isdir(os.path.join(path, folder))]

def find_txts(path):
    return [(path + "/" + txt) for txt in os.listdir(path) if txt.endswith(".txt")]


def find_filepaths(argv):
    files = []
    top_paths = find_folders(argv)
    for top_path in top_paths:
        middle_paths = find_folders(top_path)
        for middle_path in middle_paths:
            lower_paths = find_folders(middle_path)
            for lower_path in lower_paths:
                files.extend(find_txts(lower_path))
    return files


def clean_words(words):
    table = str.maketrans("", "", string.punctuation)
    cleaned = [i.translate(table) for i in words]
    cleaned = [i.lower() for i in cleaned]
    return cleaned


def get_cleaned_txt(filepath):
    output = []
    with open(filepath, 'r') as f:
        txt = f.readline()
        while txt:
            output.extend(txt.split())
            txt = f.readline()
    return clean_words(output)


# Count all the features 
def get_features(words):
    features = {}

    for word in words:
        if word in features:
            features[word] += 1
        else:
            features[word] = 1
    return features


def predict(weights, bias, example):
    features = get_features(example)
    score = 0

    for name, value in features.items():
        if name in weights:
            score += (weights[name] * value)
    score += bias
    return score


def classify_txt(argv, pos_neg_weights, pos_neg_bias, truth_decep_weights, truth_decep_bias):
    output = []
    filepaths = find_filepaths(argv)

    for filepath in filepaths:
        labels = []
        cleaned_txt = get_cleaned_txt(filepath)
        pos_neg_score = predict(pos_neg_weights, pos_neg_bias, cleaned_txt)
        truth_decep_score = predict(truth_decep_weights, truth_decep_bias, cleaned_txt)
        if truth_decep_score >= 0:
            labels.append('truthful')
        else:
            labels.append('deceptive')
        if pos_neg_score >= 0:
            labels.append('positive')
        else:
            labels.append('negative')

        output.append([labels[0], labels[1], filepath])
    return output


# Retrieve model from txt file
def get_model(modelfile):
    pos_neg_weights, truth_decep_weights = {}, {}
    pos_neg_bias, truth_decep_bias = 0, 0

    with open(modelfile, 'r') as f:
        lines = f.readlines()
        lines = lines[1:]
    
    pos_neg_bias = float(lines[0])
    lines = lines[2:]

    stop = 0
    for i in range(len(lines)):
        if lines[i][0:3] == '3 -':
            stop = i + 1
            break
        else:
            index = lines[i].find(',')
            pos_neg_weights[lines[i][:index]] = float(lines[i][index + 1:-1])
    
    truth_decep_bias = float(lines[stop])
    lines = lines[stop + 2:]

    for i in range(len(lines)):
        index = lines[i].find(',')
        truth_decep_weights[lines[i][:index]] = float(lines[i][index + 1:-1])

    return pos_neg_weights, pos_neg_bias, truth_decep_weights, truth_decep_bias


def write_output(output):
    with open('percepoutput.txt', 'w') as f:
        for i in range(len(output)):
            if i == len(output) - 1:
                f.write("{0} {1} {2}".format(output[i][0], output[i][1], output[i][2]))
            else:
                f.write("{0} {1} {2}\n".format(output[i][0], output[i][1], output[i][2]))


def main(argv):
    pos_neg_weights, pos_neg_bias, truth_decep_weights, truth_decep_bias = get_model(argv[0])
    output = classify_txt(argv[1], pos_neg_weights, pos_neg_bias, truth_decep_weights, truth_decep_bias)
    write_output(output)


if __name__ == "__main__":
    main(sys.argv[1:])
