# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 09:04:19 2024

@author: Evgeny
"""

import os, shutil
import zipfile
from os import path, utime
from time import mktime
from datetime import datetime


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
        



root_folder = 'C:/Users/Evgeny/Downloads/LabCopyFind/LabCopyFind'
source_folder = f'{root_folder}/downloads/inductance'
work_folder = f'{root_folder}/temp'


archive = '2022.02_wInd.zip'
shutil.copy2(f'{source_folder}/{archive}', f'{work_folder}/{archive}')

unpack_inplace(f'{work_folder}/{archive}')

archive = '2023.01_wInd.zip'
shutil.copy2(f'{source_folder}/{archive}', f'{work_folder}/{archive}')

unpack_inplace(f'{work_folder}/{archive}')
   