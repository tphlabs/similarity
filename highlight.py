import pymupdf  # import package PyMuPDF
import difflib


# open input PDF 
file1 = 'C:/Users/Evgeny/Documents/similarity/report/485353/rmp_Julia_62_13.pdf'
file2 = 'C:/Users/Evgeny/Documents/similarity/report/119330/rmp_mark_55_19.pdf'
#file2 = 'C:/Users/Evgeny/Documents/similarity/report/439905/rmp_ophir_30_19.pdf'

doc1 = pymupdf.open(file1)
doc2 = pymupdf.open(file2)

text1 = ' '.join([page.get_text() for page in doc1[1:]])
words1 = [word.strip() for word in text1.split()]

text2 = ' '.join([page.get_text() for page in doc2[1:]])
words2 = [word.strip() for word in text2.split()]

doc1.close()
doc2.close()


#%%

diff = difflib.ndiff(words1, words2)

def aggregate(diff):
    tokens = [token for token in diff]
    tokens.append('- end')
    result = []
    i = 0
    reset = True
    sentence = []
    while i < len(tokens)- 1:
        this_token = tokens[i]
        this_status = this_token[0] == ' '
        #print(this_token, sentence)
        if not this_status:
            i += 1
            reset = True
            #print()
            continue
        
        if reset:
            if len(sentence) >= 4:
               result.append( ' '.join(sentence) )
            #print('Result ', len(result), sentence)
            sentence = [this_token[1:]]
            reset = False
        else:
            sentence += [this_token[1:]]
            #print('.', end='')
        i +=1
    return result

result = aggregate(diff)
        

#%%

doc1 = pymupdf.open(file1)

# load desired page (0-based page number)
for page in doc1[1:]:
    print('.', end='')
    
    
    for sentence in result:
        rects = page.search_for(sentence.strip())
        if rects == None:
            continue
        if len(rects) > 1:
            p1 = rects[0].tl  # top-left point of first rectangle
            p2 = rects[-1].br  # bottom-right point of last rectangle
                
            # mark text that potentially extends across multiple lines
            page.add_highlight_annot(start=p1, stop=p2)    
            #page.add_highlight_annot(rects)
        
        
        # save the document with these changes
        filename = file1[:-4]
        newfilename = f'{filename}_yellow.pdf'
        doc1.save(newfilename)
        
doc1.close()        

        
            