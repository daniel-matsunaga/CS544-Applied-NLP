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


def classify_txt(argv, positive, negative, truthful, deceptive, pos_total, neg_total, truth_total, decep_total, vocab_total):
    output = []
    filepaths = find_filepaths(argv)

    for filepath in filepaths:
        pos, neg, truth, decep = 0,0,0,0
        labels = []
        cleaned_txt = get_cleaned_txt(filepath)
        for word in cleaned_txt:
            if word in positive:
                pos += math.log((positive[word] + 1)/ float(pos_total + vocab_total))
            else:
                pos += math.log(1 / float(pos_total + vocab_total))
            if word in negative:
                neg += math.log((negative[word] + 1) / float(neg_total + vocab_total))
            else:
                neg += math.log(1 / float(neg_total + vocab_total))
            if word in truthful:
                truth += math.log((truthful[word] + 1) / float(truth_total + vocab_total))
            else:
                truth += math.log(1 / float(truth_total + vocab_total))
            if word in deceptive:
                decep += math.log((deceptive[word] + 1) / float(decep_total + vocab_total))
            else:
                decep += math.log(1 / float(decep_total + vocab_total))

        if truth >= decep:
            labels.append('truthful')
        else:
            labels.append('deceptive')
        if pos >= neg:
            labels.append('positive')
        else:
            labels.append('negative')

        output.append([labels[0], labels[1], filepath])
    return output


# Retrieve model from txt file
def get_model(argv):
    positive, negative, truthful, deceptive = {}, {}, {}, {}
    temp = 1

    with open('nbmodel.txt', 'r') as f:
        lines = f.readlines()
        lines = lines[1:-1]
    
    vocab_total = float(lines[0])
    pos_total = float(lines[2])
    neg_total = float(lines[4])
    truth_total = float(lines[6])
    decep_total = float(lines[8])
    lines = lines[10:]

    for line in lines:
        if line[0:3] == '7 -':
            temp = 2
        elif line[0:3] == '8 -':
            temp = 3
        elif line[0:3] == '9 -':
            temp = 4
        else:
            if temp == 1:
                index = line.find(',')
                positive[line[:index]] = float(line[index + 1:-1])
            elif temp == 2:
                index = line.find(',')
                negative[line[:index]] = float(line[index + 1:-1])        
            elif temp == 3:
                index = line.find(',')
                truthful[line[:index]] = float(line[index + 1:-1])      
            elif temp == 4:
                index = line.find(',')
                deceptive[line[:index]] = float(line[index + 1:-1])      

    return positive, negative, truthful, deceptive, pos_total, neg_total, truth_total, decep_total, vocab_total


def write_output(output):
    with open('nboutput.txt', 'w') as f:
        for i in range(len(output)):
            if i == len(output) - 1:
                f.write("{0} {1} {2}".format(output[i][0], output[i][1], output[i][2]))
            else:
                f.write("{0} {1} {2}\n".format(output[i][0], output[i][1], output[i][2]))


def main(argv):
    positive, negative, truthful, deceptive, pos_total, neg_total, truth_total, decep_total, vocab_total = get_model(argv[0])
    output = classify_txt(argv[0], positive, negative, truthful, deceptive, pos_total, neg_total, truth_total, decep_total, vocab_total)
    write_output(output)

if __name__ == "__main__":
    main(sys.argv[1:])
