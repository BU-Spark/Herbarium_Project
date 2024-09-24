# Standard library imports
import os
import json
import warnings
import pickle
import ast
import shutil

# Third-party library imports
import transformers
import torch
import torch.nn as nn
import torchvision
import numpy as np
import pandas as pd
from tqdm import tqdm
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from craft_text_detector import Craft # Need to edit the saving function to prepend 0's
from torchvision import datasets

import taxonerd
from taxonerd import TaxoNERD
import spacy
import click

# Local application/library specific imports
import trocr
import detr

# from importlib import reload
# reload(detr)

# Suppress warnings
from transformers.utils import logging
logging.set_verbosity(40)
warnings.filterwarnings("ignore", "(Possibly )?corrupt EXIF data", UserWarning)

# Define CLI arguments
@click.command()
@click.option('--input-dir', required=True, type=click.Path(), help='Location of input images.')
@click.option('--save-dir', default='./', type=click.Path(), help='Location to save all output files.')
@click.option('--cache-dir', default='./', type=click.Path(), help='Location to cache all downloaded models and databases')
@click.option('--delete-intermediate', default=False, is_flag=True, help='Whether to delete intermediate files.')


def main(input_dir, save_dir, cache_dir, delete_intermediate):
    if not input_dir or not save_dir:
        print("Please specify both input_dir and save_dir!")
        return
    
    # Location of input images
    input_dir = input_dir
    # Location of images after label extraction (also input directory to CRAFT)
    workdir = '/projectnb/sparkgrp/ml-herbarium-grp/summer2023/kabilanm/ml-herbarium/trocr/label-extraction/data/intermediate-files/' # update this to the desired directory on scc

    # Location of the label extracted images
    output_dir_detr = workdir+'detr_output_files/'
    # Location of the segmentations
    output_dir_craft = workdir+'craft_output_files/'
    # Create intermediate directories
    os.makedirs(output_dir_detr)
    os.makedirs(output_dir_craft)

    # Location to save all output files
    save_dir = save_dir

    ## Running DETR to extract labels from images
    
    # Use the DETR for inference (adopted from Freddie (https://github.com/freddiev4/comp-vision-scripts/blob/main/object-detection/detr.py))
    detr_model = 'spark-ds549/detr-label-detection'
    # The DETR model returns the bounding boxes of the lables indentified from the images
    # We will utilize the bounding boxes to rank lables in the downstream task
    label_bboxes = detr.run(input_dir, output_dir_detr, detr_model)
    
    # Save the label bounding boxes into a pickle file
    pickle.dump(label_bboxes, open(save_dir+"label_boxes.pkl", "wb"))
    
    
    # we remove images with no bounding boxes found
    label_bboxes = pickle.load(open(save_dir+"label_boxes.pkl", "rb"))
    keys_to_remove = []
    
    print(f"Total number of images: {len(label_bboxes)}")
    
    for key, value in label_bboxes.items():
        if(len(value) == 0):
            keys_to_remove.append(key)
    
    for key in keys_to_remove:
        label_bboxes.pop(key)
    
    print(f"Number of images with bounding boxes: {len(label_bboxes)}")
    
    # these are the images with no bounding boxes
    print(f"Number of images without bounding boxes: {len(keys_to_remove)}")
    print(keys_to_remove)
    
    
    ## Running craft and saving the segmented images
    
    # initialize the CRAFT model
    craft = Craft(output_dir = output_dir_craft, 
                  export_extra = False, 
                  text_threshold = .7, 
                  link_threshold = .4, 
                  crop_type="poly", 
                  low_text = .3, 
                  cuda = True)
    
    # CRAFT on images to get bounding boxes
    images = []
    corrupted_images = []
    no_segmentations = []
    boxes = {}
    count= 0
    img_name = []
    box = []
    file_types = (".jpg", ".jpeg",".png")
        
    for filename in tqdm(sorted(label_bboxes.keys())):
        image = output_dir_detr+filename
        try:
            img = Image.open(image) 
            img.verify() # Check that the image is valid
            bounding_areas = craft.detect_text(image)
            if len(bounding_areas['boxes']): #check that a segmentation was found
                images.append(image)
                boxes[image] = bounding_areas['boxes']
                
            else:
                no_segmentations.append(image)
        except (IOError, SyntaxError) as e:
            corrupted_images.append(image)
    
    # Save the bounding boxes into a pickle file
    pickle.dump(boxes, open(save_dir+"boxes.pkl", "wb"))
    
    
    ## Getting all the segmented images into a dataloader, and loading model and processor for trocr
    
    # Deleting empty folders, which occurs if some of the images get no segementation from CRAFT
    root = output_dir_craft
    folders = list(os.walk(root))[1:]
    deleted = []
    for folder in folders:
        if not folder[2]:
            deleted.append(folder)
            os.rmdir(folder[0])
            
    # Setting up the TrOCR model and processor
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten", cache_dir = cache_dir)
    model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten", cache_dir = cache_dir).to(device)
    
    # Use all available gpus
    model_gpu= nn.DataParallel(model,list(range(torch.cuda.device_count()))).to(device)
    
    # Dataloader for working with gpus
    trainset = datasets.ImageFolder(output_dir_craft, transform = processor)
    testloader = torch.utils.data.DataLoader(trainset, batch_size=16, shuffle=False)
    
    # For matching words to image
    filenames = [s.replace('_crops', '') for s in list(trainset.class_to_idx)]
    
    # For matching the image name with the label name
    word_log_dic = {k: v for k,v in enumerate(filenames)}
    # For matching the image name with the transriptions
    words_identified = {k: [] for v,k in enumerate(filenames)}
    
    
    ## Saving the filenames, word_log_dic and words_identified
    
    # Save filenames
    with open(save_dir+'filenames.txt', 'w') as fp:
        for item in filenames:
            # write each item on a new line
            fp.write("%s\n" % item)
    # Save word_log_dic 
    with open(save_dir+'word_log_dic.json', 'w') as fp:
        json.dump(word_log_dic, fp)
    # Save words_identified
    with open(save_dir+'words_identified.json', 'w') as fp:
        json.dump(words_identified, fp)
    
    
    ## Running Tr-OCR on the Segmented Images from Craft
    
    #Storing the outputs
    results,confidence,labels = trocr.evaluate_craft_seg(model,processor, words_identified,word_log_dic,testloader,device)
    #Saving all the outputs in dataframe
    df = pd.DataFrame(list(zip(results,confidence,labels)),columns = ['Results','Confidence','Labels'])
    df.to_pickle(save_dir+'full_results.pkl')
    
    # First part of final csv with results, confidence level from tr-ocr, and label
    df = pd.read_pickle(save_dir+'full_results.pkl')
    boxes = pickle.load(open(save_dir+"boxes.pkl", "rb"))
    combined_df = trocr.combine_by_label(df)
    
    # Adding the image path and all bounding boxes 
    df_dictionary = pd.DataFrame(boxes.items(), columns=['Image_Path', 'Bounding_Boxes'])
    combined_df = pd.concat([combined_df, df_dictionary], axis=1, join='inner')
    
    #Save intermediate file
    combined_df.to_pickle(save_dir+'test.pkl')
    combined_df.to_csv("./combined_df.csv")
    
    
    ## Use TaxoNERD to recognize taxons from detected text
    
    ner = TaxoNERD(prefer_gpu=False) # set to "true" if GPU is accessible
    
    # utility functions for finding cosine similarity
    def word2vec(word):
        from collections import Counter
        from math import sqrt
    
        # count the characters in word
        cw = Counter(word)
        # precomputes a set of the different characters
        sw = set(cw)
        # precomputes the "length" of the word vector
        lw = sqrt(sum(c*c for c in cw.values()))
    
        # return a tuple
        return cw, sw, lw
    
    def cosdis(v1, v2):
        # which characters are common to the two words?
        common = v1[1].intersection(v2[1])
        # by definition of cosine distance we have
        return sum(v1[0][ch]*v2[0][ch] for ch in common)/v1[2]/v2[2]
    
    # Modify cache folder for taxonnerd (I changed the module codebase)
    os.environ['TAXONERD_CACHE']=cache_dir
    print(f'TaxoNERD cache directory is: {os.getenv("TAXONERD_CACHE")}')
       
    # ! pip install https://github.com/nleguillarme/taxonerd/releases/download/v1.5.0/en_core_eco_md-1.0.2.tar.gz
    
    nlp = ner.load(
        model="en_core_eco_md", # en_core_eco_
        linker="gbif_backbone",
        threshold=0 # we set the threshold to "0" so that we can collate results at various threasholds later
    )
    
    # use a transformer model from spaCy for person and location information
    nlp_loc = spacy.load("en_core_web_trf")

    # read dataframe from the pickle file saved previously
    combined_df = pickle.load(open(save_dir+"test.pkl", "rb"))

    # use TaxoNERD for entity recognition and linking against the GBIF database
    taxon_output = []
    confidence_output = []
    
    # predict taxons for text detected from each image
    for index, row in tqdm(combined_df.iterrows(), total=combined_df.shape[0]):
        try:
            # Convert the strings in the 'list_column' to actual lists
            temp = ast.literal_eval(row["Transcription"])
        except ValueError:
            temp = row["Transcription"]
    
        # construct a single string out of all the detected text
        input_text = " ".join(temp)
        doc = ner.find_in_text(input_text)
        entities = []
    
        if(input_text == ""):
            taxon_output.append("")
            confidence_output.append(float(0))
            continue
            
        try:
            # append linked taxon entity with the highest confidence
            for entity in doc.entity:
                entities.append(entity[0])
    
            result = max(entities, key=lambda x: x[2])        
            taxon_output.append(str(result[1]))
            confidence_output.append(float(result[2]))
    
        except AttributeError:
            # append empty strings when no entity is detected
            taxon_output.append("")
            confidence_output.append(float(0))
    
    # use spaCy model to recognize date and location from the text
    location_output = []
    date_output = []
    
    # predict taxons for text detected from each image
    for index, row in tqdm(combined_df.iterrows(), total=combined_df.shape[0]):
        try:
            # Convert the strings in the 'list_column' to actual lists
            temp = ast.literal_eval(row["Transcription"])
        except ValueError:
            temp = row["Transcription"]
    
        # construct a single string out of all the detected text
        input_text = " ".join(temp)
        doc_loc = nlp_loc(input_text)
        entities = []
        loc_entities = []
        date_entities = []
    
        if(input_text == ""):
            location_output.append("")
            date_output.append("")
            continue
    
        # append location and date entities recognized in the text
        for ent in doc_loc.ents:
            if(ent.label_ == "LOC"): 
                loc_entities.append(ent.text)
            if(ent.label_ == "DATE"):
                date_entities.append(ent.text)
        # print(loc_entities, date_entities)
    
    # append predicted taxon and confidence scores to the dataframe
    combined_df["Taxon_Output"] = taxon_output
    combined_df["Confidence_Output"] = confidence_output

    combined_df.to_pickle(save_dir+"full_results_with_confidence.pkl")

    print(delete_intermediate)
    if delete_intermediate:
        # Delete the intermediate folders
        shutil.rmtree(output_dir_craft)
        shutil.rmtree(output_dir_detr)
        print('\nIntermediate files deleted')

if __name__ == '__main__':
    main()
