# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 09:04:19 2024

@author: Evgeny Kolonsky
"""
#VERSION = 'v0.3.1' # 7z archives functionality added
VERSION = 'v0.4.0' # report parameters and statistics

import warnings
warnings.filterwarnings('ignore', category=FutureWarning)


import os, shutil
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from hebrew_tokenizer.tokenizer import tokenizer
import pymupdf 
import codecs
import datetime
import zipfile, py7zr
from time import mktime
import configparser
from highlight import highlight_text_in_pdf


print(f'Sumbissions similarity check {VERSION}')
print('Evgeny Kolonsky, Technion Physics, 2024 \n')


config = configparser.ConfigParser()

if  config.read('config.ini') == []:
    print('config.ini not found, creating with default parameters.')
    config['FOLDERS'] = {  'Submissions' : 'submissions',
                           'Unpack' : 'unpack',
                           'Report' : 'report'}
    
    config['PARAMETERS'] = { 'NGRAM_min': '2',
                             'NGRAM_max': '5',
                             'Threshold': '0.5',
                             'MIN_DAYS_DISTANCE': '1'}
    with open('config.ini', 'w') as configfile:
      config.write(configfile)    

print('Reading parameters from config.ini.')

root_folder = os.getcwd().replace('\\', '/')  #'C:/Users/Evgeny/Documents/similarity'
source_folder = config.get('FOLDERS', 'Submissions', fallback = 'submissions')
source_folder = f'{root_folder}/{source_folder}'

work_folder = config.get('FOLDERS', 'Unpack', fallback = 'unpack')
work_folder = f'{root_folder}/{work_folder}'

report_folder = config.get('FOLDERS', 'Report', fallback = 'report')
report_folder = f'{root_folder}/{report_folder}'

NGRAM_min = config.getint('PARAMETERS', 'NGRAM_min', fallback = 2)
NGRAM_max = config.getint('PARAMETERS', 'NGRAM_max', fallback = 5)
 
THRESHOLD = config.getfloat('PARAMETERS', 'Threshold', fallback = 0.5)  # similarity treshold
MIN_DAYS_DISTANCE = config.getint('PARAMETERS', 'MIN_DAYS_DISTANCE', fallback = 1)  # minumum time between submissions

print('Parameters read.')

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
            elif extractedfile.endswith('.7z'):
                with py7zr.SevenZipFile( extractedfile, "r") as archive:
                    archive.extractall(os.path.dirname(extractedfile))    
                
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
print('Cleaning work folder..')
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
print(f'Unpacking done. Semester to be checked: {semester_to_check}')



#%% Building model

def get_text(filename):
    extension = filename.split('.')[-1]
    if extension == 'pdf':
        doc = pymupdf.open(filename)
        text = '\n'.join([page.get_text() for page in doc])
        doc.close()
    elif extension in ['csv', 'txt', 'tsv']:
        try: 
            with open(filename, 'r') as f:
                text = f.read()
        except Exception as err:
            print(f'Exception {err} while reading file {filename}. Continued.')
            text = ''
    else:
        text = ''
    return text

   

def tokenize(text, with_whitespaces=False):
    tokenizer.with_whitespaces = with_whitespaces
    return tokenizer.tokenize(text)


def preprocess(text):
    """Preprocesses the text by removing  stop words, and stemming the words."""
    stop_words = ['']

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

print('Building text corpus ..')
attributes = build()   
print('Text corpus collection complete.')   

print('Fitting model..')

vectorizer = TfidfVectorizer(ngram_range=(NGRAM_min,NGRAM_max))

texts = [attributes[sid]["txt"] for sid in attributes.keys()]
  
tfidf = vectorizer.fit_transform(texts)
similarity = cosine_similarity(tfidf)
N = similarity.shape[0]

print('Fitting done.')

print('Building report...')

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
    
    #

    link = f'./{relative_folder}'
    shortname = submission_id
        
    if return_url_type == 'excel':
        # excel-ready version
        url = f'"=HYPERLINK( ""{link}"", ""{shortname}"")"'
    else: # html type
        url = f'"file://{link}"'
    return url, new_file_path


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
    # check only last semester
    # comment to check all semesters
    if attr_i["semester_id"] != semester_to_check:
        continue
    
    
    for j, keyj in enumerate(attributes.keys()):
        
        if i == j:
            continue
        
        cos_distance = similarity[i,j]
        if cos_distance < THRESHOLD:
            continue;

        attr_j = attributes[keyj]

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
        url1, submissionfiles1 = copy_to_report(attr_i)
        url2, submissionfiles2 = copy_to_report(attr_j)
        
        # highlight differencies for pdf
        pdfs1 = [file for file in submissionfiles1 if file.endswith('.pdf')]
        pdfs2 = [file for file in submissionfiles2 if file.endswith('.pdf')]
        if len(pdfs1) == 1 and len(pdfs2) == 1: # 1 to 1 compare available
            pdf_similar = pdfs1[0]
            pdf_source = pdfs2[0]
            
            destination_folder = f'{report_folder}/{id1}' 
            output_pdf_name = f'{id1}_{id2}.pdf'
            output_pdf_path = f'{destination_folder}/{output_pdf_name}'
            print(output_pdf_path)
            highlight_text_in_pdf(pdf_similar, pdf_source, output_pdf_path)
        # ---
        
        report += f'{sem1}\t{url1}\t{stud1}\t{dt1}\t{file1}\t{size1}\t\
                    {sem2}\t{url2}\t{stud2}\t{dt2}\t{file2}\t{size2}\t\
                    {cos_distance:.2f}\t{days_distance:.0f} \n'


# statistics
report += '\n'
report += f'Report produced: \t{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} \n'
#report += f'Submission directory: \t{source_folder}\n'
report += f'Parameters:\n'
report += f'n-grams: \t {NGRAM_min} - {NGRAM_max}\n'
report += f'Cosine distance threshold: \t {THRESHOLD}\n'
report += f'Min days distance threshold: \t {MIN_DAYS_DISTANCE}\n'
report += f'Submissions statistics:\n'
ts_total = [attributes[key]['timestamp'] for key in attributes.keys() ]
ts_tocheck = [attributes[key]['timestamp'] for key in attributes.keys() 
              if attributes[key]['semester_id'] == semester_to_check]

report += f'Checked submissions in this semester:\t {len(ts_tocheck)} \n'
report += f'Last submission date:\t {datetime.datetime.fromtimestamp(max(ts_tocheck)).strftime("%Y-%m-%d %H:%M")}\n'
report += f'Total submissions:\t {len(ts_total)}\n'
report += f'Earliest submission date:\t {datetime.datetime.fromtimestamp(min(ts_total)).strftime("%Y-%m-%d")}\n'
report += f'Source archives: \t{archives}\n'
report += f'Application version: \t{VERSION}\n'



with codecs.open(reportfilename, 'w', 'utf-8') as f:
    f.write(report)          

print('Done: see report.txt')

