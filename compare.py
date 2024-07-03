# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 09:04:19 2024

@author: Evgeny
"""

import os
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from hebrew_tokenizer.tokenizer import tokenizer
import pypdf, codecs
import datetime



root_folder = 'C:/Users/Evgeny/Downloads/LabCopyFind/LabCopyFind'
work_folder = f'{root_folder}/resistance_w'


def get_pdf_text(filename):
    reader = pypdf.PdfReader(filename)
    text = [page.extract_text() for page in reader.pages]
    return '\n'.join(text)

def get_text(filename):
    if filename.endswith('.pdf'):
        text = get_pdf_text(filename)
    elif filename.endswith('.csv'):
        with open(filename, 'r') as f:
            text = f.read()
    else:
        text = ''
    return text



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


    
def get_attributes(file_path):
    
    dirlevels = file_path.replace(work_folder,'').replace('\\', '/').split('/')
    
    moodle_name = [d for d in dirlevels if 'assignsubmission_file' in d][0].split('_')
        
    semester_id = dirlevels[1] # YYYY.NN
    filename = dirlevels[-1]
    student_name = moodle_name[0]
    submission_id = moodle_name[1]
    submission_time = os.path.getmtime(file_path)
    url = f'"file://{file_path}"'
    # excel-ready version
    url_excel = f'"=HYPERLINK( ""{file_path}"", ""{filename}"")"'
    
    txt = get_text(file_path)
    txt = preprocess(txt)
    txt_size = len(txt.split())
    
    result = {}
    result['semester_id'] = semester_id
    result['submission_id'] = submission_id
    result['student_name'] = student_name
    result['timestamp'] = submission_time
    result['url'] = url
    result['url_excel'] = url_excel
    result['file_path'] = file_path
    result['filename'] = filename
    result['txt'] = txt
    result['size_words'] = txt_size
    return result

def build():
    attributes = {}
    for dirpath, dirnames, filenames in os.walk(work_folder):
        for filename in filenames:
            file_path = f'{dirpath}/{filename}'
            attr = get_attributes(file_path)
            
            submission_id = attr['submission_id']
            
            if submission_id not in attributes.keys():
                # submission encountered for the first time
                attributes[submission_id] = attr
            else:
                # new file in existing submission
                # leave the lates timestamp
                tsnew = attr['timestamp']
                tsold = attributes[submission_id]['timestamp']
                if tsnew > tsold:
                    attributes[submission_id]['timestamp'] = tsnew
                # add filename
                attributes[submission_id]['filename'] += ', '+ attr['filename']
                # add text and size
                attributes[submission_id]['txt'] += '\n' +attr['txt']
                attributes[submission_id]['size_words'] += attr['size_words']
                # to-do : do multiple url links
            
            print('.', end='')
    print('Processed ', len(attributes))
    return attributes

attributes = build()        
texts = [attributes[sid]["txt"] for sid in attributes.keys()]


#%%
vectorizer = TfidfVectorizer(ngram_range=(2,3))
print('fitting..')
tfidf = vectorizer.fit_transform(texts)
similarity = cosine_similarity(tfidf)
print('Done')
N = similarity.shape[0]


#%%
report = 'semester \t submission_id \t student_name \t when_submitted \t filename \t url \t size_words \t\
          semester \t submission_id \t student_name \t when_submitted \t filename \t url \t size_words \t\
          cos_distance \t days_between \n'

THRESHOLD = 0.25 # similarity treshold
MIN_DAYS_DISTANCE = 1 # minumum time between submissions

semesters_checked = ['2023.01']
semesters_referenced = ['2022.02', '2022.03', '2023.01']

for i, keyi in enumerate(attributes.keys()):

    attr_i = attributes[keyi]
    
    if attr_i["semester_id"] not in semesters_checked:
        continue

    for j, keyj in enumerate(attributes.keys()):
        
        cos_distance = similarity[i,j]
        if cos_distance < THRESHOLD:
            continue;

        attr_j = attributes[keyj]
        if attr_j["semester_id"] not in semesters_referenced:
            continue

        ts1, ts2 = attr_i["timestamp"], attr_j["timestamp"]
        days_distance = (ts1 - ts2) / 60 /60 /24
        if days_distance < 0:
            days_distance = -days_distance
        
        if abs(days_distance) < MIN_DAYS_DISTANCE:
            continue
            
        dt1, dt2 = str(datetime.datetime.fromtimestamp(ts1)), \
                   str(datetime.datetime.fromtimestamp(ts2))
        
        sem1, sem2   = attr_i["semester_id"],   attr_j["semester_id"]
        id1, id2     = attr_i["submission_id"], attr_j["submission_id"]
        stud1, stud2 = attr_i["student_name"],  attr_j["student_name"]
        file1, file2 = attr_i["filename"],      attr_j["filename"]
        size1, size2 = attr_i["size_words"],    attr_j["size_words"]
        url1, url2   = attr_i["url_excel"],     attr_j["url_excel"]
        
        report += f'{sem1}\t{id1}\t{stud1}\t{dt1}\t{file1}\t{url1}\t{size1}\t\
                    {sem2}\t{id2}\t{stud2}\t{dt2}\t{file2}\t{url2}\t{size2}\t\
                    {cos_distance:.2f}\t{days_distance:.0f} \n'

with codecs.open('report.txt', 'w', 'utf-8') as f:
    f.write(report)                        

print('Done: see report.txt')