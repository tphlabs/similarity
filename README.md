# Submissions similarity search

Evgeny Kolonsky 2024

Scan submissions downloaded from Moodle site for plagiarism in folder `/submissions/[course]`.
Takes zip files named as `YYYY.NN_xxx.zip`, where `YYYY.NN` - year and semester of studies, `x` is assignment code.
The submissions of last actual semester are checked agains similarity signs in this and all previous semesters.
Results are returned to `/report` folder.

Instructions:
1. Create folder for submissions, for example submissions/pendulum.
1. Download submissions from Moodle site(s).
3. Rename zips to template YYYY.NN_xxx.zip and place to submissions folder.
4. Set configurations parameteres in config.ini:
  - FOLDERS: `submissions folder` name, `work folder` for unpacked submissions, `report folder` for placing results
  - Model PARAMETERS: `n-grams` interval (default `(2,5)`), threshold of cosine similarity from 0 (completely different) to 1 (identic texts). Default threshold `0.5`.
5. Run `compare.py` or `compare.exe`
6. See results in `report/report.txt`

To `report` folder also copied selected submissions. 
Report contains links to selected submissions, active if copy-paste text to Excel and save Excel file in the same folder. 

(under construction).
`hihglight.py` is an utility to find and higlight parts of text which is copied without changes from one pdf document to other.

Source: [https://github.com/tphlabs/similarity](https://github.com/tphlabs/similarity/edit/main/README.md)   


