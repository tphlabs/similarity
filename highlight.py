import pymupdf  # import package PyMuPDF
import difflib



# open input PDF 
pdf_path = 'C:/Users/Evgeny/Documents/similarity/report/485353/rmp_Julia_62_13.pdf'
pdf_source = 'C:/Users/Evgeny/Documents/similarity/report/119330/rmp_mark_55_19.pdf'
#file1 = 'C:/Users/Evgeny/Documents/similarity/report/248870\דוח קבל לוחות - אלון ותומר.pdf'
#file2 = 'C:/Users/Evgeny/Documents/similarity/report/398691\דוח קבל לוחות.pdf'




#%%


def extract_text_from_pdf(pdf_path):
    doc = pymupdf.open(pdf_path)
    text = ""
    for num, page in enumerate(doc):
        # unique divider to ensure split text at page break
        text += f' <<{pdf_path}_{num}>> ' + page.get_text()
    return text


def highlight_text_in_pdf(pdf_path, pdf_source, output_pdf):
    
    doc1 = pymupdf.open(pdf_path)
    doc2 = pymupdf.open(pdf_source)
    text1 = extract_text_from_pdf(pdf_path)
    text2 = extract_text_from_pdf(pdf_source)
    chain1 = text1.split()
    chain2 = text2.split()
    sequence = difflib.SequenceMatcher(None, chain1, chain2)
    matches = [match for match in sequence.get_matching_blocks() if match.size > 0]
    similar_texts = [' '.join(chain1[match.a: match.a + match.size]) for match in matches]
    
    for page in doc1:
      for text in similar_texts:
          text_instances = page.search_for(text)
          for inst in text_instances:
              highlight = page.add_highlight_annot(inst)
    #highlight.update()
    doc1.save(output_pdf)
    doc1.close()
    doc2.close()



        

#highlight_text_in_pdf(pdf_path, pdf_source)
#%%

        
            