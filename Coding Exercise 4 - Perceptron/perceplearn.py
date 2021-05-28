import sys
import os
import string
import random

# Clean words to be all lower case with no punctuation
def clean_words(words):
    table = str.maketrans("", "", string.punctuation)
    cleaned = [i.translate(table) for i in words]
    cleaned = [i.lower() for i in cleaned]
    return cleaned


# Extract all the words from the txt files
def read_txt_files(p, files, pos_neg_label, truth_decep_label): 
    text_data, pos_neg_examples, truth_decep_examples = [], [], []
    for file in files:
        if file != '.DS_Store':
            path = p + "/" + file
            output = []
            with open(path, 'r') as f:
                txt = f.readline()
                while txt:
                    output.extend(txt.split())
                    txt = f.readline()
                output = clean_words(output)
                pos_neg_examples.append([output, pos_neg_label])
                truth_decep_examples.append([output, truth_decep_label])
                text_data.extend(output)

    return text_data, pos_neg_examples, truth_decep_examples


# Retrieve txt files from the negative_polarity folder
def get_data(argv):
    text_data, pos_neg_examples, truth_decep_examples = [], [], []

    path = argv + "/negative_polarity/deceptive_from_MTurk/"
    all_folders = os.listdir(path)
    for folder in all_folders:
        if folder != '.DS_Store':
            path = argv + "/negative_polarity/deceptive_from_MTurk/" + folder
            all_files = os.listdir(path)
            text_output, pn_output, td_output = read_txt_files(path, all_files, -1, -1)
            text_data.extend(text_output)
            pos_neg_examples.extend(pn_output)
            truth_decep_examples.extend(td_output)

    path = argv + "/negative_polarity/truthful_from_Web/"
    all_folders = os.listdir(path)
    for folder in all_folders:
        if folder != '.DS_Store':
            path = argv + "/negative_polarity/truthful_from_Web/" + folder
            all_files = os.listdir(path)
            text_output, pn_output, td_output = read_txt_files(path, all_files, -1, 1)
            text_data.extend(text_output)
            pos_neg_examples.extend(pn_output)
            truth_decep_examples.extend(td_output)

    path = argv + "/positive_polarity/deceptive_from_MTurk/"
    all_folders = os.listdir(path)
    for folder in all_folders:
        if folder != '.DS_Store':
            path = argv + "/positive_polarity/deceptive_from_MTurk/" + folder
            all_files = os.listdir(path)
            text_output, pn_output, td_output = read_txt_files(path, all_files, 1, -1)
            text_data.extend(text_output)
            pos_neg_examples.extend(pn_output)
            truth_decep_examples.extend(td_output)

    path = argv + "/positive_polarity/truthful_from_TripAdvisor/"
    all_folders = os.listdir(path)
    for folder in all_folders:
        if folder != '.DS_Store':
            path = argv + "/positive_polarity/truthful_from_TripAdvisor/" + folder
            all_files = os.listdir(path)
            text_output, pn_output, td_output = read_txt_files(path, all_files, 1, 1)
            text_data.extend(text_output)
            pos_neg_examples.extend(pn_output)
            truth_decep_examples.extend(td_output)

    return text_data, pos_neg_examples, truth_decep_examples


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
    return score, features
    

def train_vanilla_perceptron(weights, bias, examples, iterations):
    for i in range(iterations):
        random.shuffle(examples)
        for example in examples:
            score, features = predict(weights, bias, example[0])
            if score * example[1] <= 0:
                for name, value in features.items():
                    if name in weights:
                        weights[name] += (example[1] * value)
                        bias += example[1]

    return weights, bias

def train_averaged_perceptron(weights, bias, c_weights, c_bias, examples, iterations):
    count = 1
    for i in range(iterations):
        random.shuffle(examples)
        for example in examples:
            score, features = predict(weights, bias, example[0])
            if score * example[1] <= 0:
                for name, value in features.items():
                    if name in weights:
                        weights[name] += (example[1] * value)
                        bias += example[1] 
                        c_weights[name] += (example[1] * count * value)
                        c_bias += (example[1] * count)               
            count += 1

    for name, value in weights.items():
        value = float(value) - (float(1 / count) * float(c_weights[name]))
    bias = float(bias) - (float(1 / count) * float(c_bias))
    
    return weights, bias


def create_model(filename, pos_neg_weights, pos_neg_bias, truth_decep_weights, truth_decep_bias):
    with open(filename, 'w') as f:
        f.write("1 - Positive + Negative Classifier Bias\n")
        f.write("{0}\n".format(str(pos_neg_bias)))

        f.write("2 - Positive + Negative Classifier Weights\n")
        for key, value in pos_neg_weights.items():
            f.write("{0},{1}\n".format(key, str(value)))

        f.write("3 - Truthful + Deceptive Classifier Bias\n")
        f.write("{0}\n".format(str(truth_decep_bias)))

        f.write("4 - Truthful + Deceptive Classifier Weights\n")
        for key, value in truth_decep_weights.items():
            f.write("{0},{1}\n".format(key, str(value)))



def main(argv):
    # Gather and clean data
    text_data, pos_neg_examples, truth_decep_examples = get_data(argv[0])
    text_data = list(dict.fromkeys(text_data))

    pos_neg_weights = dict.fromkeys(text_data, 0)
    truth_decep_weights = dict.fromkeys(text_data, 0)
    pos_neg_bias, truth_decep_bias = 0, 0


    vpn_weights, vpn_bias = train_vanilla_perceptron(pos_neg_weights, pos_neg_bias, pos_neg_examples, 400)
    vtd_weights, vtd_bias = train_vanilla_perceptron(truth_decep_weights, truth_decep_bias, truth_decep_examples, 400)

    create_model('vanillamodel.txt',vpn_weights, vpn_bias, vtd_weights, vtd_bias)

    apn_weights, apn_bias = train_averaged_perceptron(pos_neg_weights, pos_neg_bias, pos_neg_weights, pos_neg_bias, pos_neg_examples, 400)
    atd_weights, atd_bias = train_averaged_perceptron(truth_decep_weights, truth_decep_bias, truth_decep_weights, truth_decep_bias, truth_decep_examples, 400)

    create_model('averagedmodel.txt', apn_weights, apn_bias, atd_weights, atd_bias)

if __name__ == "__main__":
    main(sys.argv[1:])
