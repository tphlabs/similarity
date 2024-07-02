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
import pypdf, codecs
import datetime


def get_pdf_text(filename):
    reader = pypdf.PdfReader(filename)
    text = [page.extract_text() for page in reader.pages]
    return '\n'.join(text)

def get_text(filename):
    
    with open(filename, 'r') as f:
        text = f.read()
    return text

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


# Get a list of student files 
files = [] 
texts = []
exclusions = ['Magnetic_Field_Measurement']
    
for dirpath, dirnames, filenames in os.walk(work_folder):
    for filename in filenames:
        if any(excl in filename for excl in exclusions):
            continue
        if filename.endswith('.pdf'):
            file_path = f'{dirpath}/{filename}'
            files.append(file_path)
            txt = get_pdf_text(file_path)
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
report = 'id_i\t name_i\t dt_i\t file_i\t\
            id_j\t name_j\t dt_j\t file_j\t\
            cos_distance\t days_between \n'
THRESHOLD = 0.75
for i in range(0, N):
    print('.', end='')
    id_i, name_i, time_i, file_i = get_attributes(files[i])
    for j in range(0, i):
        id_j, name_j, time_j, file_j = get_attributes(files[j])

        if id_i == id_j:
            continue

        delta_time = time_i - time_j
        days = delta_time / 60 /60 /24 
        
        if similarity[i,j] > THRESHOLD:
            dt_i = str(datetime.datetime.fromtimestamp(time_i))
            dt_j = str(datetime.datetime.fromtimestamp(time_j))
            distance = similarity[i,j]
            report += f'{id_i}\t{name_i}\t{dt_i}\t{file_i}\t\
                        {id_j}\t{name_j}\t{dt_j}\t{file_j}\t\
                        {distance:.2f}\t{days:.0f} \n'

with codecs.open('report.txt', 'w', 'utf-8') as f:
    f.write(report)                        