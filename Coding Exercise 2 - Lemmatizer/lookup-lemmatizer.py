### This program is a very simple lemmatizer, which learns a
### lemmatization function from an annotated corpus. The function is
### so basic I wouldn't even consider it machine learning: it's
### basically just a big lookup table, which maps every word form
### attested in the training data to the most common lemma associated
### with that form. At test time, the program checks if a form is in
### the lookup table, and if so, it gives the associated lemma; if the
### form is not in the lookup table, it gives the form itself as the
### lemma (identity mapping).

### The program performs training and testing in one run: it reads the
### training data, learns the lookup table and keeps it in memory,
### then reads the test data, runs the testing, and reports the
### results.

### The program takes two command line arguments, which are the paths
### to the training and test files. Both files are assumed to be
### already tokenized, in Universal Dependencies format, that is: each
### token on a separate line, each line consisting of fields separated
### by tab characters, with word form in the second field, and lemma
### in the third field. Tab characters are assumed to occur only in
### lines corresponding to tokens; other lines are ignored.

import sys
import re

### Global variables

# Paths for data are read from command line
train_file = sys.argv[1]
test_file = sys.argv[2]

# Counters for lemmas in the training data: word form -> lemma -> count
lemma_count = {}

# Lookup table learned from the training data: word form -> lemma
lemma_max = {}

# Variables for reporting results
training_stats = ['Wordform types' , 'Wordform tokens' , 'Unambiguous types' , 'Unambiguous tokens' , 'Ambiguous types' , 'Ambiguous tokens' , 'Ambiguous most common tokens' , 'Identity tokens']
training_counts = dict.fromkeys(training_stats , 0)

test_outcomes = ['Total test items' , 'Found in lookup table' , 'Lookup match' , 'Lookup mismatch' , 'Not found in lookup table' , 'Identity match' , 'Identity mismatch']
test_counts = dict.fromkeys(test_outcomes , 0)

accuracies = {}

### Training: read training data and populate lemma counters

train_data = open (train_file , 'r')

for line in train_data:
    
    # Tab character identifies lines containing tokens
    if re.search ('\t' , line):

        # Tokens represented as tab-separated fields
        field = line.strip().split('\t')

        # Word form in second field, lemma in third field
        form = field[1]
        lemma = field[2]

        ######################################################
        ### Insert code for populating the lemma counts    ###
        if form in lemma_count:
            if lemma in lemma_count[form]:
                lemma_count[form][lemma] += 1
            else:
                lemma_count[form][lemma] = 1
        else:
            lemma_count[form] = {}
            lemma_count[form][lemma] = 1
        ######################################################

### Model building and training statistics
form_types, form_tokens = 0, 0
unambig_types, unambig_tokens = 0, 0
ambig_types, ambig_tokens = 0, 0
ambig_mct = 0
identity_tokens = 0

for form in lemma_count:

        ######################################################
        ### Insert code for building the lookup table      ###
        
        max_count = 0
        # Count word form types
        form_types += 1

        # Count unambig and ambig types
        if len(lemma_count[form]) == 1:
            unambig_types += 1
        else:
            ambig_types += 1

        for lem, lem_count in lemma_count[form].items():

            # Count word form tokens
            form_tokens += lem_count
            
            # Count identity tokens
            if form == lem:
                identity_tokens += lem_count

            # Find the most likely mapping
            if lem_count > max_count:
                max_count = lem_count
                max_lem = lem

            # Count unambig and ambig tokens
            if len(lemma_count[form]) == 1:
                unambig_tokens += lem_count
            else:
                ambig_tokens += lem_count

        # Map the lemma to the word form
        lemma_max[form] = max_lem
        if len(lemma_count[form]) > 1:
            ambig_mct += max_count
        ######################################################

        ######################################################
        ### Insert code for populating the training counts ###
training_counts['Wordform types'] = form_types
training_counts['Wordform tokens'] = form_tokens
training_counts['Unambiguous types'] = unambig_types
training_counts['Unambiguous tokens'] = unambig_tokens
training_counts['Ambiguous types'] = ambig_types
training_counts['Ambiguous tokens'] = ambig_tokens
training_counts['Ambiguous most common tokens'] = ambig_mct
training_counts['Identity tokens'] = identity_tokens
        ######################################################

### Calculate expected accuracy if we used lookup on all items ###
accuracies['Expected lookup'] = (unambig_tokens + ambig_mct) / float(form_tokens)

### Calculate expected accuracy if we used identity mapping on all items ###
accuracies['Expected identity'] = identity_tokens / float(form_tokens)

### Testing: read test data, and compare lemmatizer output to actual lemma
    
test_data = open (test_file , 'r')

test_items = 0
lookup_found, lookup_match, lookup_mismatch, lookup_notfound = 0, 0, 0, 0
identity_match, identity_mismatch = 0, 0


for line in test_data:

    # Tab character identifies lines containing tokens
    if re.search ('\t' , line):

        # Tokens represented as tab-separated fields
        field = line.strip().split('\t')

        # Word form in second field, lemma in third field
        form = field[1]
        lemma = field[2]

        ######################################################
        ### Insert code for populating the test counts     ###
        test_items += 1
        if form in lemma_max:
            lookup_found +=1
            if lemma_max[form] == lemma:
                lookup_match += 1
            else:
                lookup_mismatch += 1
        else:
            lookup_notfound += 1
            if form == lemma:
                identity_match += 1
            else:
                identity_mismatch += 1
        ######################################################

test_counts['Total test items'] = test_items
test_counts['Found in lookup table'] = lookup_found
test_counts['Lookup match'] = lookup_match
test_counts['Lookup mismatch'] = lookup_mismatch
test_counts['Not found in lookup table'] = lookup_notfound
test_counts['Identity match'] = identity_match
test_counts['Identity mismatch'] = identity_mismatch

### Calculate accuracy on the items that used the lookup table ###
accuracies['Lookup'] = lookup_match / float(lookup_found)

### Calculate accuracy on the items that used identity mapping ###
accuracies['Identity'] = identity_match / float(lookup_notfound)

### Calculate overall accuracy ###
accuracies['Overall'] = (lookup_match + identity_match) / float(test_items)

### Report training statistics and test results
                
output = open ('lookup-output.txt' , 'w')

output.write ('Training statistics\n')

for stat in training_stats:
    output.write (stat + ': ' + str(training_counts[stat]) + '\n')

for model in ['Expected lookup' , 'Expected identity']:
    output.write (model + ' accuracy: ' + str(accuracies[model]) + '\n')

output.write ('Test results\n')

for outcome in test_outcomes:
    output.write (outcome + ': ' + str(test_counts[outcome]) + '\n')

for model in ['Lookup' , 'Identity' , 'Overall']:
    output.write (model + ' accuracy: ' + str(accuracies[model]) + '\n')

output.close
