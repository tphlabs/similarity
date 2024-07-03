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


def get_pdf_text(filename):
    reader = pypdf.PdfReader(filename)
    text = [page.extract_text() for page in reader.pages]
    return '\n'.join(text)

def get_text(filename):
    if filename.endswith('.pdf'):
        text = get_pdf_text(filename)
    else:
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
    
    result = {}
    result['semester_id'] = semester_id
    result['submission_id'] = submission_id
    result['student_name'] = student_name
    result['timestamp'] = submission_time
    result['url'] = url
    result['url_excel'] = url_excel
    result['file_path'] = file_path
    result['filename'] = filename
    return result

def build():
    attributes = []
    texts = []
    for dirpath, dirnames, filenames in os.walk(work_folder):
        for filename in filenames:
            if filename.endswith('.pdf'):
                file_path = f'{dirpath}/{filename}'
                txt = get_text(file_path)
                txt = preprocess(txt)
                texts.append(txt)
                attr = get_attributes(file_path)
                
                attr["size_words"] = len(txt.split()) # tokens count
                attributes.append( attr )
                
                print('.', end='')
    print('Processed ', len(texts))
    return attributes, texts

attributes, texts = build()        


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

THRESHOLD = 0.75 # similarity treshold
MIN_DAYS_DISTANCE = 1 # minumum time between submissions

semesters_checked = ['2023.01']
semesters_referenced = ['2022.02', '2022.03']

for i in range(0, N):

    attr_i = attributes[i]
    
    if attr_i["semester_id"] not in semesters_checked:
        continue

    for j in range(0, N):
        
        cos_distance = similarity[i,j]
        if cos_distance < THRESHOLD:
            continue;

        attr_j = attributes[j]
        if attr_j["semester_id"] not in semesters_referenced:
            continue

        ts1, ts2 = attr_i["timestamp"], attr_j["timestamp"]
        days_distance = (ts1 - ts2) / 60 /60 /24 
        
        if abs(days_distance) < MIN_DAYS_DISTANCE:
            pass
            
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