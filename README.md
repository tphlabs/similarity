# Submissions similarity search

Evgeny Kolonsky v0.1 2024

Scan submissions downloaded from Moodle site for plagiarism in folder `/submissions/course`.
Takes zip files named as `YYYY.NN_xxxx.zip`, where `YYYY.NN` - year and semester of studies, `nnnn` is assignment code.
The submissions of last actual semester are checked agains similarity signs in this and all previous semesters.
Results are returned to `/report` folder.

