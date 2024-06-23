# copyfind
Plagiarizm check software sources and aixillary scripts

Instead of built-in Moodle plugin Originality, which is not working good, we have to use old-fashioned [CopyFind](https://plagiarism.bloomfieldmedia.com/software/copyfind/) for plagiarizm check.

The main advantage of CopyFind - ability to compare data-files and find cases of data stealing, which is important for data-based experiments analysis.

The process:
1. download from Moodle reference assignments from other semesters and current assignments as .zip file
2. Unpack it to flat files list with `for_copyfind.py` python script
3. configure test_script.txt
4. run Copyfind.exe < test_script
5. see report files

   
