# Evgeny Kolonsky 2024
# v 0.2
#
# Take Assignment downloaded from Moodle
# and reorganize it to flat form, suitable for
# CopyFind analysis

import os, shutil, re
import zipfile

old_semester_zipped = 'C:/Users/Evgeny/Downloads/test.zip'
old_semester_flattened = 'C:/Users/Evgeny/Downloads/test.flattened'
#old_semester_flatteted = 'C:/Users/Evgeny/Downloads/LabCopyFind/LabCopyFind/oldReports_w'
new_semester_zipped = 'C:/Users/Evgeny/Downloads/' +  'מעבדה לפיזיקה 22מ2מח2מפ - חורף-wInd-חורף - 114082-71145'
new_semester_flattened = 'C:/Users/Evgeny/Downloads/LabCopyFind/LabCopyFind/semester_w'


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
              
# flatten
def flatten(zipped_semester, new_path):
    
    shutil.copy2(zipped_semester, zipped_semester+'.backup')
    
    extracted_folder = zipped_semester + '.extracted'
    extract_nested_zip(zipped_semester, extracted_folder)
    
    extensions_allowed = ['.csv', '.py', '.ipynb']
    
    for dirpath, dirnames, filenames in os.walk(extracted_folder):
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
            new_file_path = f'{new_path}/{new_filename}'
            
            # Rename the file
            shutil.copy2(old_file_path, new_file_path)
            print(f"Renamed '{old_file_path}' to '{new_file_path}'")
    
    # restore
    shutil.copy2(zipped_semester+'.backup', zipped_semester)
    # clean up
    os.remove(zipped_semester+'.backup')
    shutil.rmtree(extracted_folder)

flatten(old_semester_zipped, old_semester_flattened)

#flatten(new_semester_in, new_semester_out)