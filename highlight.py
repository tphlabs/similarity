import pymupdf  # import package PyMuPDF
import pypdf


# open input PDF 
file1 = 'C:/Users/Evgeny/Documents/similarity/report/485353/rmp_Julia_62_13.pdf'
file2 = 'C:/Users/Evgeny/Documents/similarity/report/119330/rmp_mark_55_19.pdf'
file3 = 'C:/Users/Evgeny/Documents/similarity/report/115545/rmp_omer_63_3.pdf'

doc1 = pymupdf.open(file1)
doc2 = pymupdf.open(file2)

MIN_WORDS = 2
text1 = '\n'.join([page.get_text() for page in doc1]).replace('. ', '\n')
sentences1 = [sent.strip() for sent in text1.split('\n') if len(sent.split()) >= MIN_WORDS]

text2 = '\n'.join([page.get_text() for page in doc2]).replace('. ', '\n')
sentences2 = [sent.strip() for sent in text2.split('\n') if len(sent.split()) >= MIN_WORDS]

#%%


# load desired page (0-based page number)
for page in doc1:
    print('.', end='')
    
    for sentence in sentences2:
        rects = page.search_for(sentence)
    
        page.add_highlight_annot(rects)
        
        
        # save the document with these changes
        doc1.save("output.pdf")