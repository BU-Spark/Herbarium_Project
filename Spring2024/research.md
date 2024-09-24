# Phase 2: Research and Problem Understanding

#### by George Trammell, Andy Xie, Max Karambelas (02/25/2024)

This document summarizes our preliminary research for the task of improving Chinese character OCR for the Harvard University Herbaria. Our primary goal is to test the implementation of certain OCR models which are specifically suited for the task in order to improve the accuracy of Chinese OCR both locally and in the cloud.


## Noteworthy Resources

<u>**Tesseract**</u> is an [LSTM-based](https://colah.github.io/posts/2015-08-Understanding-LSTMs/) Google-sponsored open source OCR engine boasting a giant ecosystem and high-quality OCR in most languages.

-   [An Overview of the Tesseract OCR Engine](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/33418.pdf)
    
-   [Project Repository](https://github.com/tesseract-ocr/tesseract)
    
-   [Documentation](https://tesseract-ocr.github.io/tessdoc/Command-Line-Usage.html#simplest-invocation-to-ocr-an-image)
  
Advantages: Highly versatile and widely supported with a large supporting community. [Performs well on multilingual OCR tasks](https://dl.acm.org/doi/abs/10.1145/1577802.1577804).

<br />

<u>**PaddleOCR**</u>, an OCR model from the open-source ecosystem [PaddlePaddle](https://www.paddlepaddle.org.cn/en), has several models which specialize in Chinese/English OCR.

-   [Relevant OCR models](https://aistudio.baidu.com/modelsoverview?task=Optical%20Character%20Recognition&sortBy=weight)
    
-   [Project Repository](https://github.com/PaddlePaddle/PaddleOCR)
    
-   [Documentation (English)](https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.7/README_en.md)
    
Advantages: Fast and lightweight models, often suitable for mobile and web applications. Top performance in OCR benchmarks for Chinese characters.


## Modified Project Plan

Our primary goal is to increase the accuracy of the TrOCR model on Chinese characters using models built specifically for the task, including (but not limited to):
- PaddleOCR, a Chinese-made model specifically designed for recognizing Chinese and English characters
- TesseractOCR, a longstanding open-source LSTM-based OCR model
- Existing cloud-based tools or APIs to see if we can get a higher baseline accuracy for our local models

The previous team attempted to use [MaskOCR](https://arxiv.org/pdf/2206.00311.pdf), a model which uses a masked autoencoder during its pretraining phase. While this approach reported high accuracy on common English language testing sets, the model is unlikely to help us improve performance on Chinese OCR, and its codebase is still not publicly available.
    

## Performance Criteria

-   Measure accuracy metrics against existing TrOCR-based models.
    
-   Measure accuracy metrics against commercial OCR models.
    
-   Measure cost per thousand of inferences/predictions versus commercial OCR models.
    

## Deliverable Artifacts

- An improved OCR model on Chinese characters and handwritten Chinese characters.
    
- An ML Ops Pipeline:
	- Perform data version control on Heberia Dataset.
	- Maintain the:
		1. Segmentation from scanned images
		2. Classification on Chinese printed characters or Chinese handwritten characters or other languages
		3. OCR task on Chinese printed characters or Chinese handwritten characters ML pipeline
	- Integration on CI/CD.
    

## Other Research

**Levenshtein OCR**
[Paper](https://arxiv.org/pdf/2209.03594v2.pdf)
[Project](https://github.com/AlibabaResearch/AdvancedLiterateMachinery/tree/main/OCR/LevOCR)
<br />

**DTrOCR – Decoder-only Transformer for Optical Character Recognition**
[Paper](https://arxiv.org/pdf/2308.15996v1.pdf)
[Project](https://github.com/Swall0w/dtrocr)
<br />

**Benchmarking Chinese Text Recognition - Datasets, Baselines, and an Empirical Study**
[Paper](https://arxiv.org/pdf/2112.15093.pdf)
[Project](https://github.com/FudanVI/benchmarking-chinese-text-recognition)
<br />

**CASIA Handwritten Chinese Datasets (Hanzi)**
[Datasets](https://www.kaggle.com/datasets/pascalbliem/handwritten-chinese-character-hanzi-datasets)
<br />

**awesome-chinese-nlp**
[Project](https://github.com/crownpku/awesome-chinese-nlp)
<br />

**Easter 2.0 – Improving Convolutional Models for Handwritten Text Recognition**
[Paper](https://arxiv.org/pdf/2205.14879v1.pdf)
[Project](https://github.com/kartikgill/easter2)