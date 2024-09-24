# Proof of Concept - Deployment Plan

# File Descriptions
---
> ## Codebase on SCC
> Some folders from the codebase, such as logs and data folders, have **NOT been pushed to GitHub**. The most up-to-date codebase (along with all accompanying files and folders) **on SCC** can be found at the path `/projectnb/sparkgrp/ml-herbarium-grp/summer2023/kabilanm/ml-herbarium/`.
---
This directory contains all of the files associated with the Tr-OCR pipeline.

## trocr_with_detr_label_extraction.ipynb
This notebook shows the process of setting up DETR to identify labels in each image and CRAFT for segmentation, extracting all bounding boxes around text within the bounding boxes from DETR. These segmented images are then passed through the TrOCR model to perform text recognition; we save the transcriptions and model confidence for each of these calculations. Then, we perform entity recognition and linking against a database of taxons (in order to find the best match for each.  All of this information is then accrued in a final output dataframe, which contains the bounding boxes and transcriptions for every segmentation. We then test the accuracy of the pipeline on roughly 250 images at different confidence thresholds.

## cleaned_trocr_test.ipynb
This notebook is identical to the above notebook, except it does not include the DETR model.

# Model Deployment Files
## trocr_with_detr_transcription.py
This is the **main (inference)** script for running the pipeline. This script performs several operations, such as object detection, text extraction, and Named Entity Recognition (NER) on a set of images. 

1. First, it initializes and runs a model called DETR to identify labels in each image and save their bounding boxes to a pickle file.
2. Second, it runs a text detection model called CRAFT on the images to identify areas containing text, saving these bounding areas to another pickle file.
3. Third, it sets up a text recognition model called TrOCR and runs it on the text areas identified by CRAFT, storing the results in a DataFrame and saving it to a pickle file.
4. Fourth, it uses TaxoNERD, an NER tool, to identify taxon names within the text recognized by TrOCR, adding these identifications and their confidence scores to the DataFrame.

Note that this script uses command-line interface (CLI) options to specify input/output directories and other parameters as below.
- `--input-dir`: Specifies the location of the input images. Required argument.
- `--save-dir`: Specifies the directory where all output files will be saved. Default is the current directory (`./`).
- `--cache-dir`: Specifies the directory for caching downloaded models and databases. Default is the current directory (`./`).
- `--delete-intermediate`: A flag that, when used, will delete all intermediate files created during the process.

If you want to specify the input and output directories, for example, you would run:

```
python trocr_with_detr_transcription.py --input-dir /path/to/input --save-dir /path/to/output
```

If you also want to delete the intermediate files after the script runs, you'd include the `--delete-intermediate` flag:

```
python trocr_with_detr_transcription.py --input-dir /path/to/input --save-dir /path/to/output --delete-intermediate
```

## trocr.py
Contains all the functions which relate to running the trocr portion of the pipeline

## [Not in use] utilities.py
Contains a number of functions which are primarily related to the included CVIT_Training.py file.

## [Not in use] requirements.txt
All required python installs for running the pipeline

## trocr_env.yml
Conda environment configuration to run the pipeline.

# Deployment instructions
Optional: Create a new directory and cd into it

```
mkdir new_directory
cd new_directory
```
Git clone the ml-herbarium repo
```
git clone https://github.com/BU-Spark/ml-herbarium.git
cd ml-herbarium
git checkout dev
cd trocr
```
Create a new conda environment with the environment YAML file and activate it
```
conda env create -n my-conda-env --file=trocr_env.yml
conda activate my-conda-env
```

Install Jupyter and required packages
```
conda install jupyter
pip install transformers==4.27.0 --no-deps
```
We install the `transformers` package separately because of the dependency requirement that is imposed by `spacy-transformers`. The dependency does not cause any issues, albeit throwing an installation error.

Currently, the setup uses `en_core_eco_md` (and `en_core_eco_biobert`) models for entity recognition as part of the TaxoNERD pipeline. To download and add the models, run the following commands.
```
pip install https://github.com/nleguillarme/taxonerd/releases/download/v1.5.0/en_core_eco_md-1.0.2.tar.gz
pip install https://github.com/nleguillarme/taxonerd/releases/download/v1.5.0/en_core_eco_biobert-1.0.2.tar.gz
```
Other available models can be viewed [here](https://github.com/nleguillarme/taxonerd#models). Respective model installation instructions can be found [here](https://github.com/nleguillarme/taxonerd#models:~:text=To%20download%20the%20models%3A).

To use the spaCy models for extracting location and date information, please run the following commands.
```
python -m spacy download en_core_web_sm
python -m spacy download en_core_web_md
python -m spacy download en_core_web_trf
```

To start Jupyter Notebooks in the current folder, use the command
```
jupyter notebook
```

To run the pipeline, please execute the [`trocr_with_detr_label_extraction.ipynb`](https://github.com/BU-Spark/ml-herbarium/blob/research-doc-patch/trocr/trocr_with_detr_label_extraction.ipynb) notebook in the current (`trocr`) folder.

> **For docker deployment instructions, refer to the `docker` folder in the current (`trocr`) folder.**

> **NOTE:** It is HIGHLY recommended to run the pipeline on a GPU (V100(16 GB) on SCC is recommended so that multiple models in the pipeline can be hosted on the GPU; smaller GPUs have not been tested). Running on the CPU is significantly slower.

## Final Dataframe Column Descriptions
### Label
This column describes the position that a given image was processed
### Transcription
This column contains every transcription that was found in the image. They are ordered based on the relative position of the top left coordinate for each bounding box in an image. 
## Transcription_Confidence
This contains the TrOCR model confidences in each transcription. This list of values is ordered based on the `Transcription` column (i.e., you can reference each individual transcription and its confidence using the same index number).
## Image_Path
This is the absolute path of the location for a given image
## Bounding_Boxes
This contains the coordinates of each bounding box found in an image. Exactly like transcription confidence, these lists can be indexed based on positions in the `Transcription` column. 
## Taxon_Output
This contains the taxons predicted by the entity linking step in the TaxoNerd pipeline.
## Confidence_Output
This contains the confidence for taxons predicted by the entity linking step in the TaxoNerd pipeline.

## Evaluation Dataframe Column Descriptions
## Confidence_Threshold
This column contains the confidence threshold use for entity linking in the TaxoNerd pipeline. 
## Num_Taxons_Correct
This column contains the number of taxons **correctly** predicted at each `Confidence_Threshold` (from 0 to 1 at 0.1 intervals).
## Num_Taxons_Predicted
This column contains the number of taxons predicted at each `Confidence_Threshold` (from 0 to 1 at 0.1 intervals).
## Taxons_Accuracy_Predicted
This column contains the number of taxons predicted with a cosine similarity score of `>0.8` at each `Confidence_Threshold`.
