import pandas as pd
import os
import re
import csv
import random
#import spacy




def convert_all_files_to_csv(folder_path = 'reviews/'):
    for filename in os.listdir(folder_path):
        if filename.endswith(".xlsx"):
            file_path = os.path.join(folder_path, filename)

            # Load the XLSX file
            try:
                df = pd.read_excel(file_path)

                # Create the CSV file name
                csv_file = os.path.splitext(file_path)[0] + '.csv'

                # Convert the XLSX file to CSV
                df.to_csv(csv_file, index=False ,encoding= 'utf-8-sig')
            except:
                print ("unable to convert" + file_path)

def extract_quotes(sentence):
    pattern = r'"(.*)"\s\((.*)\)'
    match = re.search(pattern, sentence)

    if match is not None:
        quote = match.group(1)
        person = match.group(2)
        return True, quote, person
    else:
        return False,'',''



def extract_sentences(source_file):
    with open(source_file) as in_f:
        for line in in_f:
            line= line.strip('\"')
            if len(line) == 0:
                pass
            full_reviews.append(line)
            for l in line.split('.'):
                is_quote, quote, person = extract_quotes(l)
                regex = r'\w+\s+(יקר|יקרה|היקר|היקרה)\b'
                pattern = re.compile(regex)
                if re.search(regex, l) is not None:
                    l = pattern.sub('', l)
                    if not is_quote:
                        starting_sentences.append(l)
                if is_quote:
                    quotes.append((quote, person))
                else:
                    items.append(l)







def prepare_data(folder_path = 'reviews/'):
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            print(filename)
            file_path = os.path.join(folder_path, filename)
            extract_sentences(file_path)

            with open("train_dataset.txt", 'w', encoding='utf-8-sig', newline='') as train_f:
                with open("test_dataset.txt", 'w' ,encoding= 'utf-8-sig', newline='') as test_f:
                    for line in full_reviews:
                        if random.randrange(0,100)<85:
                            train_f.write(line.strip(' \"'))
                        else:
                            test_f.write(line.strip(' \"'))

"""
            with open("starting_sentences.csv", 'w' ,encoding= 'utf-8-sig', newline='') as out_f:
                writer = csv.writer(out_f)
                for line in starting_sentences:
                    writer.writerow([line])

            with open("quotes.csv", 'w',encoding= 'utf-8-sig', newline='') as out_f:
                writer = csv.writer(out_f)
                for quote, person in quotes:
                    writer.writerow([quote, person])

            with open("raw_reviews.csv", 'w',encoding= 'utf-8-sig', newline='') as out_f:
                writer = csv.writer(out_f)
                for line in items:
                    writer.writerow([line])
"""

convert_all_files_to_csv('reviews/')


starting_sentences, quotes, items, full_reviews= [],[],[],[]
prepare_data( 'reviews/')





