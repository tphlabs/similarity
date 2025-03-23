import pymupdf  # import package PyMuPDF
from pymupdf.utils import getColor
import difflib

from PIL import Image, ImageChops
from io import BytesIO
import  imagehash
import numpy as np

# version 0.2.1 refactored hash comparison

MIN_PIXEL_SIZE = 300
HASH_DISTANCE_THRESHOLD = 8

#%%
# version 0.2 with graphics

def extract_text_from_pdf(doc):
    text = ""
    for num, page in enumerate(doc):
        # unique divider to ensure split text at page break
        text += f' <<page_{num}>> ' + page.get_text(sort=True)
    return text



    

# returns list of image hash for all images in pdf document
def extract_images_from_pdf(doc):
    # trims white spaces around image for the following reason:
    # white space may slighltly vary when image is copy-pasted
    # from original document to a copy document
    def trim(im):
        bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
        diff = ImageChops.difference(im, bg)
        diff = ImageChops.add(diff, diff, 2.0, -100)
        bbox = diff.getbbox()
        if bbox:
            return im.crop(bbox)
        else:
            return im
        
    def image_blank(img):
        extrema = img.convert("L").getextrema()  
        #print(extrema)
        #img.show()
        return  extrema[0] == extrema[1]
        
    
    images = {}
    for page in doc:
        for block in page.get_text("dict")["blocks"]:
            # skip if no image block
            if block["type"] != 1:
                continue
            w = block['width']            
            h = block['height']
            if  w < MIN_PIXEL_SIZE or h < MIN_PIXEL_SIZE:
                continue
            id = block['number']
            img_data = block['image']                    
            img = Image.open(BytesIO(img_data))
            
            # skip empy image
            if image_blank(img):
                continue
            
            img = trim(img)
            
            #fname = f'{doc.name}_{id}.jpg'
            #print(fname)
            #img.save(fname)
            
            try:
                images[id] =  {'hash' :imagehash.average_hash(img, hash_size=16),
                               'image': img }
            except:
                pass
    return images


def hashes_compare(images1, images2):
# gets images dict
# returns keys of images1 having similar image in images2

    similar_pairs = set([ (id1, id2)
                  for id1 in images1 
                  for id2 in images2 
                  if images1[id1]['hash'] - images2[id2]['hash'] <= HASH_DISTANCE_THRESHOLD])
    # set of pic ids found be copied in image 1
    ids0 = set([pair[0] for pair in similar_pairs]) 
    # and the same for image 2
    ids1 = set([pair[1] for pair in similar_pairs])
    return similar_pairs, ids0, ids1




def highlight_text_in_pdf(pdf_path, pdf_source, output_pdf):
    
    doc1 = pymupdf.open(pdf_path)
    doc2 = pymupdf.open(pdf_source)
    
    # text highlight
    text1 = extract_text_from_pdf(doc1)
    text2 = extract_text_from_pdf(doc2)
    chain1 = text1.split()
    chain2 = text2.split()
    sequence = difflib.SequenceMatcher(None, chain1, chain2)
    matches = [match for match in sequence.get_matching_blocks() if match.size > 1]
    similar_texts = [' '.join(chain1[match.a: match.a + match.size]) for match in matches]
    
    
    
    for page in doc1:
      for text in similar_texts:
          text_instances = page.search_for(text)
          for inst in text_instances:
              try: 
                  highlight = page.add_highlight_annot(inst)
                  #pass
              except Exception as err:
                  print(f'Exception {err} while annotating {pdf_path}. Continued.')
                  continue
    #highlight.update()
    
    #image highlight
    images1 = extract_images_from_pdf(doc1)
    images2 = extract_images_from_pdf(doc2)
    
    similar_pairs, ids1, ids2 = hashes_compare(images1, images2)
    for page in doc1:
        for pic in page.get_image_info():
            # skip if no image block
            if pic['number'] in ids1:
                bbox = pic['bbox']
                page.draw_rect(bbox, color=getColor("yellow"))
    doc1.save(output_pdf)
    doc1.close()
    doc2.close()


#%%

if __name__ == "__main__":
    # open input PDF 
    pdf_path = 'c:/Users/Evgeny/Downloads/r1.pdf'
    pdf_source = 'c:/Users/Evgeny/Downloads/r2.pdf'
    output = 'c:/Users/Evgeny/Downloads/3.pdf'        

    print('Highliting..')

    highlight_text_in_pdf(pdf_path, pdf_source, output)

    print('done')        
            