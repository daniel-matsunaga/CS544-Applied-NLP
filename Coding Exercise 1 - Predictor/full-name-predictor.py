import sys
from csv import reader
import csv

# Splits the test names into the first part (names1) and second part (names2) and saves the original
def get_testdata_names(argv):
    names1, names2, original_names = [], [], []

    with open(argv[0], 'r') as names_data_obj:
        names_data = reader(names_data_obj)
        for row in names_data:
            lst = row[0].split()
            original_names.append(row)
            for i in range(len(lst)):
                if lst[i] == 'AND':
                    names1.append(lst[:i])                        
                    names2.append(lst[i+1:])
                    break
            
    return names1, names2, original_names


# Retrieves first names and surnames and their rankings in dictionaries
def get_database_names():
    male_names, female_names, surnames = {}, {}, {}

    count = 0
    with open('MaleNames.csv', 'r') as male_data_obj:
        male_data = reader(male_data_obj)
        for row in male_data:
            if count == 0:
                male_names[row[0][1:]] = float(row[1])
            count +=1
            male_names[row[0]] = float(row[1])

    count = 0
    with open('FemaleNames.csv', 'r') as female_data_obj:
        female_data = reader(female_data_obj)
        for row in female_data:
            if count == 0:
                female_names[row[0][1:]] = float(row[1])
            count += 1
            female_names[row[0]] = float(row[1])

    count = 0
    with open('Names_2010Census.csv', 'r') as surname_data_obj:
        surname_data = reader(surname_data_obj)
        for row in surname_data:
            if count > 0:
                surnames[row[0]] = float(row[3]) / 1000
            count += 1

    return male_names, female_names, surnames

# Convert a list to a string so output is formatted correctly
def list_to_str(names):
    s = " "
    return (s.join(names))

# First part of the name was not the full name, so check the second part of the names and return the predicted last name
def check_names2(male_names, female_names, surnames, n2):
    n2_2last = n2[-2]

    if n2_2last not in male_names and n2_2last not in female_names:
        # n2_2last is a surname
        return list_to_str(n2[-2:])
    elif n2_2last in surnames and n2_2last in male_names and n2_2last in female_names: 
        if surnames[n2_2last] - 0.01 >= male_names[n2_2last] and surnames[n2_2last] - 0.01 >= female_names[n2_2last]:
            return list_to_str(n2[-2:])
    elif n2_2last in surnames and n2_2last in male_names:
        if surnames[n2_2last] - 0.01 >= male_names[n2_2last]:
            return list_to_str(n2[-2:])
    elif n2_2last in surnames and n2_2last in female_names:
        if surnames[n2_2last] - 0.01 >= female_names[n2_2last]:
            return list_to_str(n2[-2:])

    return list_to_str(n2[-1:])


# Compare test data names to statistic data and output predicted full names
def get_key_names(names1, names2, male_names, female_names, surnames):
    key_names = []

    for n1, n2 in zip(names1, names2):

        n1_last = n1[-1]
        if n1[0] == 'DOCTOR' or n1[0] == 'PROFESSOR' or n1[0] == 'REVEREND' or n1[0] == 'MAJOR' or n1[0] == 'COLONEL':
            n1_first = n1[1]
        else:
            n1_first = n1[0]


        if len(n1) == 1:
            # Good Rule - 3 errors
            n1.append(check_names2(male_names, female_names, surnames, n2))
            key_names.append(list_to_str(n1)) 
        elif len(n1) == 2 and len (n2) == 2:
            #  errors
            if n1_last not in male_names and n1_last not in female_names:
                # surname
                key_names.append(list_to_str(n1)) 
            elif n1_first in female_names and n1_first not in male_names and n1_last in male_names and n1_last not in female_names:
                key_names.append(list_to_str(n1))
            elif n1_first in male_names and n1_first not in female_names and n1_last in female_names and n1_last not in male_names:
                key_names.append(list_to_str(n1))
            elif n1_last in surnames and n1_last in male_names and n1_last in female_names:
                if surnames[n1_last] - 0.01 >= male_names[n1_last] and surnames[n1_last] - 0.01 >= female_names[n1_last]:
                    key_names.append(list_to_str(n1))  
                else:
                    n1.append(n2[1])
                    key_names.append(list_to_str(n1))                      
            elif n1_last in surnames and n1_last in male_names:
                if surnames[n1_last] - 0.01 >= male_names[n1_last]:
                    key_names.append(list_to_str(n1)) 
                else:
                    n1.append(n2[1])
                    key_names.append(list_to_str(n1))     
            elif n1_last in surnames and n1_last in female_names:  
                if surnames[n1_last] - 0.01 >= female_names[n1_last]:
                    key_names.append(list_to_str(n1)) 
                else:
                    n1.append(n2[1])
                    key_names.append(list_to_str(n1)) 
            else:
                n1.append(n2[1])
                key_names.append(list_to_str(n1))                        
        elif len(n1) > 2 and len(n2) == 2:
            # Good Rule - 1 error
            if n1[0] == 'DOCTOR' or n1[0] == 'PROFESSOR' or n1[0] == 'REVEREND' or n1[0] == 'MAJOR' or n1[0] == 'COLONEL':
                n1.append(check_names2(male_names, female_names, surnames, n2))
                key_names.append(list_to_str(n1))  
            else:
                key_names.append(list_to_str(n1)) 
        elif len(n1) == 2 and len(n2) > 2:
            # Test More
            if n1_last not in male_names and n1_last not in female_names:
                # surname
                key_names.append(list_to_str(n1)) 
            elif n1_first in female_names and n1_first not in male_names and n1_last in male_names and n1_last not in female_names:
                key_names.append(list_to_str(n1))
            elif n1_first in male_names and n1_first not in female_names and n1_last in female_names and n1_last not in male_names:
                key_names.append(list_to_str(n1))
            elif n1_last in surnames and n1_last in male_names and n1_last in female_names:
                if surnames[n1_last] - 0.01 >= male_names[n1_last] and surnames[n1_last] - 0.01 >= female_names[n1_last]:
                    key_names.append(list_to_str(n1))  
                else:
                    n1.append(check_names2(male_names, female_names, surnames, n2))
                    key_names.append(list_to_str(n1))  
            elif n1_last in surnames and n1_last in male_names:
                if surnames[n1_last] - 0.01 >= male_names[n1_last]:
                    key_names.append(list_to_str(n1)) 
                else:
                    n1.append(check_names2(male_names, female_names, surnames, n2))
                    key_names.append(list_to_str(n1))     
            elif n1_last in surnames and n1_last in female_names:  
                if surnames[n1_last] - 0.01 >= female_names[n1_last]:
                    key_names.append(list_to_str(n1)) 
                else:
                    n1.append(check_names2(male_names, female_names, surnames, n2))
                    key_names.append(list_to_str(n1)) 
            else:
                n1.append(check_names2(male_names, female_names, surnames, n2))
                key_names.append(list_to_str(n1))       
        elif len(n1) > 2 and len(n2) > 2:
            # 0 errors
            if len(n1) > 3 and (n1[0] == 'DOCTOR' or n1[0] == 'PROFESSOR' or n1[0] == 'REVEREND' or n1[0] == 'MAJOR' or n1[0] == 'COLONEL'):
                key_names.append(list_to_str(n1))
            elif n1[0] != 'DOCTOR' and n1[0] != 'PROFESSOR' and n1[0] != 'REVEREND' and n1[0] != 'MAJOR' and n1[0] != 'COLONEL':
                key_names.append(list_to_str(n1))
            else:
                if n1_last not in male_names and n1_last not in female_names:
                    # surname
                    key_names.append(list_to_str(n1)) 
                elif n1_last in surnames and n1_last in male_names and n1_last in female_names:
                    if surnames[n1_last] - 0.01 >= male_names[n1_last] and surnames[n1_last] - 0.01 >= female_names[n1_last]:
                        key_names.append(list_to_str(n1))  
                    else:
                        n1.append(check_names2(male_names, female_names, surnames, n2))
                        key_names.append(list_to_str(n1))  
                elif n1_last in surnames and n1_last in male_names:
                    if surnames[n1_last] - 0.01 >= male_names[n1_last]:
                        key_names.append(list_to_str(n1)) 
                    else:
                        n1.append(check_names2(male_names, female_names, surnames, n2))
                        key_names.append(list_to_str(n1))     
                elif n1_last in surnames and n1_last in female_names:  
                    if surnames[n1_last] - 0.01 >= female_names[n1_last]:
                        key_names.append(list_to_str(n1)) 
                    else:
                        n1.append(check_names2(male_names, female_names, surnames, n2))
                        key_names.append(list_to_str(n1)) 
                else:
                    n1.append(check_names2(male_names, female_names, surnames, n2))
                    key_names.append(list_to_str(n1))      
        else:
            n1.append(check_names2(male_names, female_names, surnames, n2))
            key_names.append(list_to_str(n1))   
 
    return key_names
        

# Create the output csv file
def write_output(original_names, key_names):
    output_names = []
    for name, key in zip(original_names, key_names):
        output_names.append([name[0], key])

    with open('full-name-output.csv', 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(output_names)

def test_output():
    keys, output = [], []

    with open('dev-key.csv', 'r') as key_data_obj:
        key_data = reader(key_data_obj)
        for row in key_data:
            keys.append(row[1])
            
    with open('full-name-output.csv', 'r') as output_data_obj:
        output_data = reader(output_data_obj)
        for row in output_data:
            output.append(row[1])
    
    count = 0
    for key, out in zip(keys, output):
        if key == out:
            count += 1
        elif out != " ":
            print(out + "\t\t\tkey: " + key)
    accuracy = count/1000.0
    print(accuracy)


def main(argv):
    # Read input test data csv and split the first and seconds parts
    names1, names2, original_names = get_testdata_names(argv)

    # Create dictionaries of database names and their popularity rankings
    male_names, female_names, surnames = get_database_names()

    # Create list of predicted names
    key_names = get_key_names(names1, names2, male_names, female_names, surnames)

    # Write to output csv file
    write_output(original_names, key_names)

    # Test accuracy
    test_output()
    

if __name__ == "__main__":
    main(sys.argv[1:])