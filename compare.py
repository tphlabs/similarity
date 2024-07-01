# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 09:04:19 2024

@author: Evgeny
"""

import os
from nltk.corpus import stopwords
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from hebrew_tokenizer.tokenizer import tokenizer


root_folder = 'C:/Users/Evgeny/Downloads/LabCopyFind/LabCopyFind'
work_folder = f'{root_folder}/temp'


def tokenize(text, with_whitespaces=False):
    tokenizer.with_whitespaces = with_whitespaces
    return tokenizer.tokenize(text)


def preprocess(text):
    """Preprocesses the text by removing non-alphabetic characters, stop words, and stemming the words."""
    stop_words = set(stopwords.words('hebrew'))

    tokens = tokenize(text.lower())
    tokens = [token[1] for token in tokens if  token[1] not in stop_words]
    return ' '.join(tokens)


#nltk.download('stopwords')
#nltk.download('punkt')





def get_text(filename):
    
    with open(filename, 'r') as f:
        text = f.read()
    return text

# Get a list of student files 
files = [] 
texts = []
exclusions = ['Magnetic_Field_Measurement']
    
for dirpath, dirnames, filenames in os.walk(work_folder):
    for filename in filenames:
        if any(excl in filename for excl in exclusions):
            continue
        if filename.endswith('.csv'):
            file_path = f'{dirpath}/{filename}'
            files.append(file_path)
            txt = get_text(file_path)
            txt = preprocess(txt)
            texts.append(txt)
            print('.', end='')
print('Processed ', len(files))
            
#%%
vectorizer = TfidfVectorizer()
print('fitting..')
tfidf = vectorizer.fit_transform(texts)
similarity = cosine_similarity(tfidf)
print('Done')
N = similarity.shape[0]

#%%
def get_attributes(file_path):
    dirlevels = file_path.replace('\\', '/').split('/')
    try:
        attributes = [d for d in dirlevels if 'assignsubmission_file' in d][0].split('_')
    except:
        print('Error: ', dirlevels)
    filename = dirlevels[-1]
    student_name = attributes[0]
    submission_id = attributes[1]
    submission_time = os.path.getmtime(file_path)
    return submission_id, student_name, submission_time, filename            
#%%
THRESHOLD = 0.75
for i in range(0, N):
    print('.', end='')
    id_i, name_i, time_i, file_i = get_attributes(files[i])
    for j in range(0, i):
        id_j, name_j, time_j, file_j = get_attributes(files[j])

        if id_i == id_j:
            continue

        delta_time = abs(time_i - time_j)
        days = delta_time / 60 /60 /24 
        if days <7:
            continue
        
        if similarity[i,j] > THRESHOLD:
            print()
            print(f'{name_i}, {name_j}, {similarity[i,j]:.2f}, {days:.0f} {file_i} {file_j}')