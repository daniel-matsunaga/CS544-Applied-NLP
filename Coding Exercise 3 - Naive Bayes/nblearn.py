import sys
import os
import string


# Extract all the words from the txt files
def read_txt_files(p, files):
    output = []

    for file in files:
        if file != '.DS_Store':
            path = p + "/" + file
            with open(path, 'r') as f:
                txt = f.readline()
                while txt:
                    output.extend(txt.split())
                    txt = f.readline()
    return output

# Retrieve txt files from the negative_polarity folder
def get_negative_data(argv):
    truthful_negative, deceptive_negative = [], []

    path = argv + "/negative_polarity/deceptive_from_MTurk/"
    all_folders = os.listdir(path)
    for folder in all_folders:
        if folder != '.DS_Store':
            path = argv + "/negative_polarity/deceptive_from_MTurk/" + folder
            all_files = os.listdir(path)
            deceptive_negative.extend(read_txt_files(path, all_files))

    path = argv + "/negative_polarity/truthful_from_Web/"
    all_folders = os.listdir(path)
    for folder in all_folders:
        if folder != '.DS_Store':
            path = argv + "/negative_polarity/truthful_from_Web/" + folder
            all_files = os.listdir(path)
            truthful_negative.extend(read_txt_files(path, all_files))

    return truthful_negative, deceptive_negative


# Retrieve txt files from the positive_polarity folder
def get_positive_data(argv):
    truthful_positive, deceptive_positive = [], []

    path = argv + "/positive_polarity/deceptive_from_MTurk/"
    all_folders = os.listdir(path)
    for folder in all_folders:
        if folder != '.DS_Store':
            path = argv + "/positive_polarity/deceptive_from_MTurk/" + folder
            all_files = os.listdir(path)
            deceptive_positive.extend(read_txt_files(path, all_files))

    path = argv + "/positive_polarity/truthful_from_TripAdvisor/"
    all_folders = os.listdir(path)
    for folder in all_folders:
        if folder != '.DS_Store':
            path = argv + "/positive_polarity/truthful_from_TripAdvisor/" + folder
            all_files = os.listdir(path)
            truthful_positive.extend(read_txt_files(path, all_files))

    return truthful_positive, deceptive_positive


def clean_words(words):
    table = str.maketrans("", "", string.punctuation)
    cleaned = [i.translate(table) for i in words]
    cleaned = [i.lower() for i in cleaned]
    return cleaned

def create_classifier(words, vocabulary):
    classifier = {}
    total = 0
    words = clean_words(words)

    for word in words:
        if word in classifier:
            classifier[word] += 1
        else:
            classifier[word] = 1
        if word not in vocabulary:
            vocabulary.append(word)
        total += 1
    
    return classifier, total, vocabulary


def create_model(positive, negative, truthful, deceptive, total_pos, total_neg, total_truth, total_decep, total_vocab):
    with open('nbmodel.txt', 'w') as f:
        f.write("1 - Total vocabulary size\n")
        f.write("{0}\n".format(str(total_vocab)))

        f.write("2 - Size of vocabulary for positive class\n")
        f.write("{0}\n".format(str(total_pos)))

        f.write("3 - Size of vocabulary for negative class\n")
        f.write("{0}\n".format(str(total_neg)))

        f.write("4 - Size of vocabulary for truthful class\n")
        f.write("{0}\n".format(str(total_truth)))

        f.write("5 - Size of vocabulary for deceptive class\n")
        f.write("{0}\n".format(str(total_decep)))

        f.write("6 - Counts of text observations given positive class\n")
        for key, value in positive.items():
            f.write("{0},{1}\n".format(key, str(value)))

        f.write("7 - Counts of text observations given negative class\n")
        for key, value in negative.items():
            f.write("{0},{1}\n".format(key, str(value)))

        f.write("8 - Counts of text observations given truthful class\n")
        for key, value in truthful.items():
            f.write("{0},{1}\n".format(key, str(value)))

        f.write("9 - Counts of text observations given deceptive class\n")
        for key, value in deceptive.items():
            f.write("{0},{1}\n".format(key, str(value)))


def main(argv):
    truthful_negative, deceptive_negative = get_negative_data(argv[0])
    truthful_positive, deceptive_positive = get_positive_data(argv[0])

    positive = []
    positive.extend(deceptive_positive)
    positive.extend(truthful_positive)

    negative = []
    negative.extend(deceptive_negative)
    negative.extend(truthful_negative)

    truthful = []
    truthful.extend(truthful_negative)
    truthful.extend(truthful_positive)

    deceptive = []
    deceptive.extend(deceptive_positive)
    deceptive.extend(deceptive_negative)

    vocabulary = []
    pos_classifier, pos_total, vocabulary = create_classifier(positive, vocabulary)
    neg_classifier, neg_total, vocabulary = create_classifier(negative, vocabulary)
    truth_classifier, truth_total, vocabulary = create_classifier(truthful, vocabulary)
    decep_classifier, decep_total, vocabulary = create_classifier(deceptive, vocabulary)

    create_model(pos_classifier, neg_classifier, truth_classifier, decep_classifier, pos_total, neg_total, truth_total, decep_total, len(vocabulary))


if __name__ == "__main__":
    main(sys.argv[1:])
