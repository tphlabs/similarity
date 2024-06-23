# modified

import os
import shutil


#root_directory = 'C:/Users/Evgeny/Downloads/מעבדה לפיזיקה 22מ2מח2מפ - אביב.02-pdfInd-181386'
#new_path = 'C:/Users/Evgeny/Downloads/LabCopyFind/LabCopyFind/oldReports'
root_directory = 'C:/Users/Evgeny/Downloads/suspect'
new_path = 'C:/Users/Evgeny/Downloads/LabCopyFind/LabCopyFind/semester'

# modified

for dirpath, dirnames, filenames in os.walk(root_directory):
    for i, filename in enumerate(filenames):
        # Construct the old file path
        old_file_path = os.path.join(dirpath, filename)
        extension = os.path.splitext(filename)[1]
        parentdir = dirpath.split('\\')[-1]
        student_id = parentdir.split('_')[1]
        student_name = parentdir.split('_')[0]
        # Construct the new filename
        new_filename = f"{student_id}_{student_name}_{i}{extension}"
        
        # Construct the new file path
        new_file_path = f'{new_path}/{new_filename}'
        
        # Rename the file
        shutil.copy2(old_file_path, new_file_path)
        print(f"Renamed '{old_file_path}' to '{new_file_path}'")

