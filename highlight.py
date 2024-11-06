import pymupdf  # import package PyMuPDF
from pymupdf.utils import getColor
import difflib

from PIL import Image, ImageOps, ImageChops
from io import BytesIO
import  imagehash
import numpy as np



MIN_PIXEL_SIZE = 300
HASH_DISTANCE_THRESHOLD = 8

#%%
# version 0.2 with graphics

def extract_text_from_pdf(doc):
    text = ""
    for num, page in enumerate(doc):
        # unique divider to ensure split text at page break
        text += f' <<page_{num}>> ' + page.get_text()
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
            img = trim(img)    
            try:
                images[id] =  {'hash' :imagehash.average_hash(img, hash_size=16),
                               'image': img }
            except:
                pass
    return images


def pairwise_compare(images1, images2):
# gets pair of hashes vector h1, h2
# for each element in h1 searches similar image hash in h2
# when found excludes the pair found and continues to search
# returns tuple (count, N)
# where count - number of elements in h1 having similar elements in h2
# and N - total number of elements in h1
    
    def nearest_hash(hsh, v):
    # gets hash hsh and vector of hashes v
    # returns index of element in v
    # having hash nearest to hsh
    # if distance between them is small enough
        Nv = len(v)
        ind = -1 # default
        if Nv > 0:
            distance = np.zeros(Nv) - 1
            for i in range(Nv):
                distance[i] = hsh - v[i]
            if np.min(distance) <= HASH_DISTANCE_THRESHOLD:
                ind = np.argmin(distance)
        return ind
    
    hashes1 = [images1[id]['hash'] for id in images1.keys()]
    hashes2 = [images2[id]['hash'] for id in images2.keys()]
    similar_pairs = {}
    Nh = len(hashes1)
    count = 0
    h2copy = hashes2.copy()
    for im in images1.keys():
        key2 = nearest_hash(images1[im]['hash'], h2copy)
        if key2 >= 0: # found similar image in hashes2
            count += 1
            similar_pairs[im] = 0 # images2[key2]
            # remove image that was found similiar from further comparison
            h2copy = [x for i,x in enumerate(h2copy) if i !=  key2]
            if len(h2copy) > 0: 
                continue
            else:
                break
    return similar_pairs




def highlight_text_in_pdf(pdf_path, pdf_source, output_pdf):
    
    doc1 = pymupdf.open(pdf_path)
    doc2 = pymupdf.open(pdf_source)
    
    # text highlight
    text1 = extract_text_from_pdf(doc1)
    text2 = extract_text_from_pdf(doc2)
    chain1 = text1.split()
    chain2 = text2.split()
    sequence = difflib.SequenceMatcher(None, chain1, chain2)
    matches = [match for match in sequence.get_matching_blocks() if match.size > 0]
    similar_texts = [' '.join(chain1[match.a: match.a + match.size]) for match in matches]
    
    for page in doc1:
      for text in similar_texts:
          text_instances = page.search_for(text)
          for inst in text_instances:
              try: 
                  highlight = page.add_highlight_annot(inst)
              except Exception as err:
                  print(f'Exception {err} while annotating {pdf_path}. Continued.')
                  continue
    #highlight.update()
    
    #image highlight
    images1 = extract_images_from_pdf(doc1)
    images2 = extract_images_from_pdf(doc2)
    similar_pairs = pairwise_compare(images1, images2)
    for page in doc1:
        for pic in page.get_image_info():
            # skip if no image block
            if pic['number'] in similar_pairs.keys():
                bbox = pic['bbox']
                page.draw_rect(bbox, color=getColor("yellow"))
    doc1.save(output_pdf)
    doc1.close()
    doc2.close()


#%%
# open input PDF 
#pdf_path = 'c:/Users/Evgeny/Downloads/1.pdf'
#pdf_source = 'c:/Users/Evgeny/Downloads/2.pdf'
#output = 'c:/Users/Evgeny/Downloads/3.pdf'        

#highlight_text_in_pdf(pdf_path, pdf_source, output)

        
            