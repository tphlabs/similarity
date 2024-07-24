# Submissions similarity search 

Evgeny Kolonsky 2024

This app searches student's report and data submissions uploaded to Moodle site for plagiarism by calculating text similarity with previous reports.
The similarity is a cosine distance number from 0 to 1, where 1 for identical text and 0 for completely different texts.
Reports in format .pdf are highlighted to show copied fragments of text.

Application runs in command line. All parameters are configured in config.ini file.

Submission as .zip archive are read from  `/submissions/[assignment]` folder. 
Zip files should be renamed for better readability as `YYYY.NN_xxx.zip`, where `YYYY.NN` - year and semester of studies, `xxx` is assignment code.
The submissions of last actual semester are checked against submissions in all previous semesters.
Results are returned to `/report` folder.

Instructions:
1. Create folder for submissions, for example submissions/pendulum.
1. Download submissions from Moodle site(s).
3. Rename zips to template YYYY.NN_xxx.zip and place to submissions folder.
4. Set configurations parameters in config.ini:
  - FOLDERS: `submissions folder` name, `work folder` for unpacked submissions, `report folder` for placing results
  - Model PARAMETERS: `n-grams` interval (default `(2,5)`), threshold of cosine similarity from 0 (completely different) to 1 (identic texts). Default threshold `0.5`.
5. Run `compare.exe`
6. See results in `report/report.txt`

To `report` folder also copied selected submissions. 
Report contains links to selected submissions, active if copy-paste text to Excel and save Excel file in the same folder. 


Source: [https://github.com/tphlabs/similarity](https://github.com/tphlabs/similarity/edit/main/README.md)   


