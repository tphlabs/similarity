# Evgeny Kolonsky 2024
# v 0.3
#
# Take Assignment downloaded from Moodle
# and reorganize it to flat form, suitable for
# CopyFind analysis

import os, shutil, re
import zipfile

temp_folder = 'C:/Users/Evgeny/Desktop\LabCopyFind/temp'
corpus_downloads = 'C:/Users/Evgeny/Downloads/LabCopyFind/LabCopyFind/downloads/capacitor'
corpus_flattened = 'C:/Users/Evgeny//Downloads/LabCopyFind/LabCopyFind//assignments/capacitor'

# files are located in following structure
# folder XXXX.XX semester ID
# one or more .zip files with assignments: workfiles and reports
# first we have to unpack all files to a flat structure, having semster_id, student_id, student_name, file_name and extension in ling-file-name


# extract zip
def extract_nested_zip(zippedFile, toFolder):
    """ Extract a zip file including any nested zip files
        Delete the zip file(s) after extraction
    """
    with zipfile.ZipFile(zippedFile, 'r') as zfile:
        zfile.extractall(path=toFolder)
    os.remove(zippedFile)
    for root, dirs, files in os.walk(toFolder):
        for filename in files:
            if re.search(r'\.zip$', filename):
                fileSpec = os.path.join(root, filename)
                extract_nested_zip(fileSpec, root)
              

def flatten_extracted(from_folder, to_folder, extensions_allowed):
    
    for dirpath, dirnames, filenames in os.walk(from_folder):
        for filename in filenames:
            # Construct the old file path
            old_file_path = os.path.join(dirpath, filename)
            extension = os.path.splitext(filename)[1]
            
            if extension not in extensions_allowed:
                continue
            
            parentdir = dirpath.split('\\')[1]
            student_id = parentdir.split('_')[1]
            student_name = parentdir.split('_')[0]
            # Construct the new filename
            new_filename = f"{student_id}_{student_name}_{filename}"
            new_filename = new_filename.replace('=', '_')
            new_filename = new_filename.replace(' ', '_')
            #if extension == '.csv':
            #    new_filename += '.txt'
            
            # Construct the new file path
            new_file_path = f'{to_folder}/{new_filename}'
            
            # Rename the file
            shutil.copy2(old_file_path, new_file_path)
            print(f"Renamed '{old_file_path}' to '{new_file_path}'")
    
# flatten
def extractzip_and_flatten(zipped_semester, new_path):
    
    shutil.copy2(zipped_semester, zipped_semester+'.backup')
    
    extracted_folder = zipped_semester + '.extracted'
    extract_nested_zip(zipped_semester, extracted_folder)
    
    extensions_allowed = ['.csv', '.py', '.ipynb']
    
    flatten_extracted(extracted_folder, new_path, extensions_allowed)
    
    # restore
    shutil.copy2(zipped_semester+'.backup', zipped_semester)
    # clean up
    os.remove(zipped_semester+'.backup')
    shutil.rmtree(extracted_folder)

###########################################

# unzip files from downloads directory to tree-shaped extracted structure
# place it in folders in temporary folder

# clean up
shutil.rmtree(temp_folder)
os.mkdir(temp_folder)

for dirpath, dirnames, filenames in os.walk(corpus_downloads):
    
    for filename in filenames:
        # Construct the old file path
        semester_id = dirpath.split('\\')[-1]
        assignment_type = filename.split('-')[-2]
        file_path = os.path.join(dirpath, filename)
        extension = os.path.splitext(filename)[-1]
        #print(semester_id, file_path, extension)
        destination_folder = f'{temp_folder}/{semester_id}_{assignment_type}'
        
        if extension == '.zip':
            destination_file = f'{temp_folder}/{filename}'
            shutil.copy2(file_path, destination_file)
            print('unzipping ')
            extract_nested_zip(destination_file, destination_folder)
        else:
            destination_file = f'{destination_folder}/{filename}'
            shutil.copy2(file_path, destination_file)
                
            
extensions_allowed = ['.csv', '.pdf']

from_folder = temp_folder
to_folder = corpus_flattened
    
for dirpath, dirnames, filenames in os.walk(from_folder):
    for filename in filenames:
        # Construct the old file path
        old_file_path = os.path.join(dirpath, filename)
        extension = os.path.splitext(filename)[1]
        
        if extension not in extensions_allowed:
            continue
        
        ASF_name = dirpath.split('\\')[-1] # אביחי פרץ_398748_assignsubmission_file_'
        ASF_student_name = ASF_name.split('_')[0] # אביחי פרץ
        ASF_id = ASF_name.split('_')[1] # פרץ_398748_assignsubmission_file_
        ASF_semester_type = dirpath.split('\\')[2] # 2022.02_pdfC
        
#        student_id = parentdir.split('_')[1]
#        student_name = parentdir.split('_')[0]
        # Construct the new filename
        new_filename = f"{ASF_semester_type}_{ASF_id}_{ASF_student_name}_{filename}"
        new_filename = new_filename.replace('=', '_')
        new_filename = new_filename.replace(' ', '_')
        #if extension == '.csv':
        #    new_filename += '.txt'
        
        # Construct the new file path
        new_dir_path = f'{to_folder}/{ASF_semester_type}'
        new_file_path = f'{new_dir_path}/{new_filename}'
        
        # Rename the file
        try:
            shutil.copy2(old_file_path, new_file_path)
        except:
            os.mkdir(new_dir_path)
            shutil.copy2(old_file_path, new_file_path)
        # print(f"Renamed '{old_file_path}' to '{new_file_path}'")
                
            


