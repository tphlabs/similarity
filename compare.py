# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 09:04:19 2024

@author: Evgeny
"""

import os, shutil
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from hebrew_tokenizer.tokenizer import tokenizer
import pypdf, codecs
import datetime
import zipfile
from time import mktime
import configparser


config = configparser.ConfigParser()
config.read('config.ini')


root_folder = os.getcwd().replace('\\', '/')  #'C:/Users/Evgeny/Documents/similarity'
source_folder = f'{root_folder}/{config["FOLDERS"]["Submissions"]}'

work_folder = f'{root_folder}/{config["FOLDERS"]["Unpack"]}'
report_folder = f'{root_folder}/{config["FOLDERS"]["Report"]}'

NGRAM_min = int(config["PARAMETERS"]["NGRAM_min"])
NGRAM_max = int(config["PARAMETERS"]["NGRAM_max"])
 
THRESHOLD = float(config["PARAMETERS"]["Threshold"]) # similarity treshold
MIN_DAYS_DISTANCE = float(config["PARAMETERS"]["MIN_DAYS_DISTANCE"]) # minumum time between submissions

#%% Unpacking

def unpack_inplace(zippedFile):
    
    path = os.path.dirname(zippedFile)
    
    with zipfile.ZipFile(zippedFile, 'r') as zfile:

        for zi in zfile.infolist():
            
            extractedfile = zfile.extract(zi,path=path)
            
            # preserve creation time
            date_time = mktime(zi.date_time + (0, 0, -1))
            os.utime(extractedfile, (date_time, date_time))
            
            if extractedfile.endswith('.zip'):
                unpack_inplace(extractedfile)

    os.remove(zippedFile)
    
    return
        

def copy_unpack(archive, source_folder, work_folder):
    
    semester_id = archive.split('_')[0]  # 2023.01_rmp.zip
    destination_folder = f'{work_folder}/{semester_id}'
    
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
        
    shutil.copy2(f'{source_folder}/{archive}', f'{destination_folder}/{archive}')
    unpack_inplace(f'{destination_folder}/{archive}')
    return


# clean up work folder
if os.path.exists(work_folder):
    shutil.rmtree(work_folder)
os.makedirs(work_folder)

print('Unpacking..')
archives = [file for file in os.listdir(source_folder) if file.endswith('.zip')]
for archive in sorted(archives):
    if archive.endswith('.zip'):
        print(archive)
        copy_unpack(archive, source_folder, work_folder)
        
# last archive in sorted list is the semester to be checked
semester_to_check = archive.split('_')[0]



#%% Building model

def get_text(filename):
    try:
        if filename.endswith('.pdf'):
            reader = pypdf.PdfReader(filename)
            text = '\n'.join([page.extract_text() for page in reader.pages])
        elif filename.endswith('.csv'):
            with open(filename, 'r') as f:
                text = f.read()
        else:
            text = ''
    except Exception as error:
        print(f'Exception {error} while reading {filename}.')
        text = ''
    return text

   

def tokenize(text, with_whitespaces=False):
    tokenizer.with_whitespaces = with_whitespaces
    return tokenizer.tokenize(text)


def preprocess(text):
    """Preprocesses the text by removing  stop words, and stemming the words."""
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
    
    txt = get_text(file_path)
    txt = preprocess(txt)
    txt_size = len(txt.split())
    
    result = {}
    result['semester_id'] = semester_id
    result['submission_id'] = submission_id
    result['student_name'] = student_name
    result['timestamp'] = submission_time
    result['file_path'] = [file_path]
    result['filename'] = [filename]
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
                # list concat
                attributes[submission_id]['filename'] += attr['filename']
                attributes[submission_id]['file_path'] += attr['file_path'] 
                # add text and size
                attributes[submission_id]['txt'] += '\n' +attr['txt']
                attributes[submission_id]['size_words'] += attr['size_words']
            
            print('.', end='')
    print('Processed ', len(attributes))
    return attributes

attributes = build()        
texts = [attributes[sid]["txt"] for sid in attributes.keys()]

vectorizer = TfidfVectorizer(ngram_range=(NGRAM_min,NGRAM_max))
print('fitting..')
tfidf = vectorizer.fit_transform(texts)
similarity = cosine_similarity(tfidf)
print('Done')
N = similarity.shape[0]


#%% Reporting result

def copy_to_report(attr, return_url_type='excel'):
    
    submission_id = attr['submission_id']
    student_name = attr['student_name']
    
    #relative_folder = f'{submission_id}_{student_name}'.replace(' ', '_')
    relative_folder = f'{submission_id}'
    destination_folder = f'{report_folder}/{relative_folder}'
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    new_file_path = [shutil.copy(file_path, destination_folder) for file_path in attr['file_path'] ]

    link = f'./{relative_folder}'
    shortname = submission_id
        
    if return_url_type == 'excel':
        # excel-ready version
        url = f'"=HYPERLINK( ""{link}"", ""{shortname}"")"'
    else: # html type
        url = f'"file://{link}"'
    return url


report = 'semester \t submission_id \t student_name \t when_submitted \t filename \t size_words \t\
          semester \t submission_id \t student_name \t when_submitted \t filename \t size_words \t\
          cos_distance \t days_between \n'



# clean up report folder
if os.path.exists(report_folder):
    shutil.rmtree(report_folder)
os.makedirs(report_folder)
   
reportfilename = f'{report_folder}/report.txt'


for i, keyi in enumerate(attributes.keys()):

    attr_i = attributes[keyi]
    
    if attr_i["semester_id"] != semester_to_check:
        continue

    for j, keyj in enumerate(attributes.keys()):
        
        if i == j:
            continue
        
        cos_distance = similarity[i,j]
        if cos_distance < THRESHOLD:
            continue;

        attr_j = attributes[keyj]
        #if attr_j["semester_id"] not in semesters_referenced:
        #    continue

        ts1, ts2 = attr_i["timestamp"], attr_j["timestamp"]
        days_distance = (ts1 - ts2) / 60 /60 /24
        if days_distance < MIN_DAYS_DISTANCE:
            continue
            
        dt1, dt2 = str(datetime.datetime.fromtimestamp(ts1)), \
                   str(datetime.datetime.fromtimestamp(ts2))
                   
        
        sem1, sem2   = attr_i["semester_id"],   attr_j["semester_id"]
        id1, id2     = attr_i["submission_id"], attr_j["submission_id"]
        stud1, stud2 = attr_i["student_name"],  attr_j["student_name"]
        file1, file2 = attr_i["filename"],      attr_j["filename"]
        size1, size2 = attr_i["size_words"],    attr_j["size_words"]

        # copy to report folder
        url1 = copy_to_report(attr_i)
        url2 = copy_to_report(attr_j)
        
        report += f'{sem1}\t{url1}\t{stud1}\t{dt1}\t{file1}\t{size1}\t\
                    {sem2}\t{url2}\t{stud2}\t{dt2}\t{file2}\t{size2}\t\
                    {cos_distance:.2f}\t{days_distance:.0f} \n'


with codecs.open(reportfilename, 'w', 'utf-8') as f:
    f.write(report)          

print('Done: see report.txt')

