# -*- coding: utf-8 -*-
"""
Created on Wed Jun 11 08:01:16 2025

@author: Evgeny
"""

import configparser
import os

config = configparser.ConfigParser()

if  config.read('config.ini') == []:
    print('config.ini not found, creating with default parameters.')
    config['FOLDERS'] = {  'Submissions' : 'submissions',
                           'Unpack' : 'unpack',
                           'Report' : 'report'}
    
    config['PARAMETERS'] = {'THRESHOLD_PERCENTILE': '95',
                            'MIN_DAYS_DISTANCE': '14',
                            'ALLOWED_IMAGES_COPIED': '2',
                            'HASH_DISTANCE_THRESHOLD': '16',
                            'MIN_PIXEL_SIZE': '300',
                            'HASH_SIZE': '16',
                            'NGRAM_min': '2',
                             'NGRAM_max': '5'
                             }
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


THRESHOLD_PERCENTILE = config.getfloat('PARAMETERS', 'THRESHOLD_PERCENTILE', fallback = 95)  # similarity treshold
MIN_DAYS_DISTANCE = config.getint('PARAMETERS', 'MIN_DAYS_DISTANCE', fallback = 14)  # minumum time between submissions
ALLOWED_IMAGES_COPIED = config.getint('PARAMETERS', 'ALLOWED_IMAGES_COPIED', fallback=2) # similar images  treshold
HASH_DISTANCE_THRESHOLD = config.getint('PARAMETERS', 'HASH_DISTANCE_THRESHOLD', fallback=16) # similar images  treshold
MIN_PIXEL_SIZE = config.getint('PARAMETERS', 'MIN_PIXEL_SIZE', fallback=300) # min width or height in pixels
HASH_SIZE =  config.getint('PARAMETERS', 'HASH_SIZE', fallback=16) # image hash table size
NGRAM_MIN = config.getint('PARAMETERS', 'NGRAM_min', fallback = 2)
NGRAM_MAX = config.getint('PARAMETERS', 'NGRAM_max', fallback = 5)
    
print('Parameters read.')
