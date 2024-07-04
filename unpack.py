# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 09:04:19 2024

@author: Evgeny
"""

import os, shutil
import zipfile
from time import mktime

root_folder = 'C:/Users/Evgeny/OneDrive - Technion/Documents/similarity'
source_folder = f'{root_folder}/downloads/pendulum'
work_folder = f'{root_folder}/unpacked'



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




archive = '2023.01_rmp.zip'
#copy_unpack(archive, source_folder, f'{work_folder}/{2023.01}')
copy_unpack(archive, source_folder, work_folder)

archive = '2023.02_rmp.zip'
#copy_unpack(archive, source_folder, f'{work_folder}/{2023.02}')
copy_unpack(archive, source_folder, work_folder)



'''
archive = '2022.03_pdfInd.zip'
copy_unpack(archive, source_folder, f'{work_folder}/{2022.03}')

archive = '2022.02_pdfInd.zip'
copy_unpack(archive, source_folder, f'{work_folder}/{2022.02}')

archive = '2023.01_pdfInd.zip'
copy_unpack(archive, source_folder, f'{work_folder}/{2023.01}')


# workfiles csv
archive = '2022.02_wR.zip'
copy_unpack(archive, source_folder, f'{work_folder}/{2022.02}')

archive = '2022.03_wR.zip'
copy_unpack(archive, source_folder, f'{work_folder}/{2022.03}')

archive = '2023.01_wR.zip'
copy_unpack(archive, source_folder, f'{work_folder}/{2023.01}')

# report files pdf
archive = '2022.02_pdfR.zip'
copy_unpack(archive, source_folder, f'{work_folder}/{2022.02}')

archive = '2022.03_pdfR.zip'
copy_unpack(archive, source_folder, f'{work_folder}/{2022.03}')

archive = '2023.01_pdfR.zip'
copy_unpack(archive, source_folder, f'{work_folder}/{2023.01}')
'''