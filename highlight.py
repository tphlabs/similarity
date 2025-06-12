import pymupdf  # import package PyMuPDF
from pymupdf.utils import getColor
import difflib

from PIL import Image, ImageChops
from io import BytesIO
import  imagehash
import numpy as np

from config import HASH_DISTANCE_THRESHOLD, MIN_PIXEL_SIZE, HASH_SIZE

# version 0.2.1 refactored hash comparison
# version 0.2.2 with matches > 0


#%%
# version 0.2 with graphics


def extract_text_from_pdf(doc):
    text = ""
    for num, page in enumerate(doc):
        # unique divider to ensure split text at page break
        text += f' <<{doc.name}_{num}>> ' + page.get_text(sort=True)
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
    for pagenum, page in enumerate(doc):
        for block in page.get_text("dict")["blocks"]:
            # skip if no image block
            if block["type"] != 1:
                continue
            bbox = block['bbox']
            #w1 = block['width']            
            #h1 = block['height']
            x0, y0, x1, y1 = bbox[0], bbox[1], bbox[2], bbox[3]
            w = x1 - x0
            h = y1 - y0
            if  (w < MIN_PIXEL_SIZE) or (h < MIN_PIXEL_SIZE):
                # debug
                #print(f'Skipped {w:.0f}, {h:.0f}')
                continue
            
            id = f'{pagenum}_{block["number"]}'
            img_data = block['image']                    
            img = Image.open(BytesIO(img_data))
            #print(img.size)
            
            # skip empy image
            if image_blank(img):
                # debug
                #print(f'{doc}_{page}{id} image blank')
                continue
            
            ## debug
            img = trim(img)
            
            ############## debug
            #fname = f'{doc.name}_{id}.png'
            #print(fname)
            #img.convert('RGBA').save(f'{fname}')
            #######################
            
            try:
                images[id] =  {'hash' :imagehash.phash(img, hash_size=HASH_SIZE),
                               'image': img,
                               'bbox': bbox,
                               'size': (w, h)}
            except:
                print(f'Failed to get hash image {doc.name}_{id}')
                pass
    #print(f'{doc} {len(images)}')
    return images


def hashes_compare(images1, images2):
# gets images dict
# returns keys of images1 having similar image in images2
    if len(images1) * len(images2) ==0:
        return []
    
    # index to key map
    ix1 = {}
    for i, key in enumerate(images1): 
        ix1[i] = key
    ix2 = {}
    for i, key in enumerate(images2): 
        ix2[i] = key
        
    # distance matrix
    hash_dist = np.array([ 
                    [ images1[id1]['hash'] - images2[id2]['hash'] for id2 in images2 ]
                        for id1 in images1 ] )
    # find the nearest image by it's index
    nearest_ix = np.argmin(hash_dist, axis=1)
    nearest_dist = np.min(hash_dist, axis=1)
    
    # remap index to image id for min distances below treshold
    similar_images = [(ix1[i], ix2[nearest_ix[i]]) for i in range(len(nearest_ix))
             if nearest_dist[i] < HASH_DISTANCE_THRESHOLD]
    
    return similar_images




def highlight_pdf(pdf_path, pdf_source, output_pdf):
    
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
    
    similar_images = hashes_compare(images1, images2)
    
    
    for pagenum, page in enumerate(doc1):
        #for pic in page.get_image_info():
        for block in page.get_text("dict")["blocks"]:            
            if block["type"] != 1:
                continue
            pic = block
            id = f'{pagenum}_{pic["number"]}'
            page.draw_rect(pic['bbox'], color=getColor("gray"))
            #page.add_freetext_annot(pic['bbox'], f'{id}')
            
            if id in [pair[0] for pair in similar_images]:
                rect = pic['bbox']
                page.draw_rect(rect, color=getColor("yellow"))
                page.add_freetext_annot(rect, f'{id}')
                ## debug
                pairs = [pair for pair in similar_images if pair[0] == id]      
                #print(f'Image {doc1}_{pic["number"]} is found in {pairs}')
                id1 = pairs[0][0]
                id2 = pairs[0][1]
                img1 = images1[id1]['image']
                img2 = images2[id2]['image']
                ## insert thumbnail image
                # get annotated image rect coordinates
                x0, y0, x1, y1 = rect[0], rect[1], rect[2], rect[3]
                w = x1 - x0
                h = y1 - y0
                # calculate thumbnail coordinates - left side of the page and twice small
                x0_, y0_ = 1, y0 - 10
                x1_, y1_ = x0_ + w/2, y0_ + h/2
                # top 
                topleft = (x0_, y0_)  
                bottomright = (x1_, y1_) 
                clip = pymupdf.Rect(topleft, bottomright)  # the area we want            
                # place here thumbnail of the similar image 
                stream = BytesIO()
                img2.save(stream, format='PNG')
                stream.seek(0)
                image_bytes = stream.read()
                page.insert_image(clip, stream=image_bytes)
                page.draw_rect(clip, color=getColor("red"))

                # annotate
                fullname  = doc2.name
                shortname = fullname.split('/')[-1]
                page.add_freetext_annot(clip, f'Source:\n{shortname} {id2}')

                
                
    doc1.save(output_pdf)
    doc1.close()
    doc2.close()
    
    return similar_texts, similar_images, images1, images2


#%%

if __name__ == "__main__":
    # open input PDF 
    pdf_path = 'c:/Users/Evgeny/Downloads/n1.pdf'
    pdf_source = 'c:/Users/Evgeny/Downloads/n2.pdf'
    output = 'c:/Users/Evgeny/Downloads/n3.pdf'        

    print('Highliting..')

    similar_texts, similar_images, images1, images2 = highlight_pdf(pdf_path, pdf_source, output)

    print('done')        
            