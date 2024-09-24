# Technical Project Document 
### George Trammell, Max Karambelas, Andy Xie - 2024-Feb-8 0.0.1-dev
## Overview
In this document, based on the available project outline and summary of the project pitch, to the best of your abilities, you will come up with the technical plan or goals for implementing the project such that it best meets the stakeholder requirements.

A. Provide a solution in terms of human actions to confirm if the task is within the scope of automation through AI.
Manually identifying and segmenting the label from the herbarium sheet.
Reading and transcribing the text from the label, which includes taxon, geography, collection code, barcode, location, date collected, collector name, collector number, and habitat.
Entering the transcribed data into a database.
Validating the accuracy of the transcription against known data.

B. Problem Statement:
The project aims to automate the transcription of handwritten labels from herbarium specimens into a digital format. Specifically, it is a machine learning problem that involves developing and improving OCR (Optical Character Recognition) models, with a focus on LSTM-RNN and Transformer-based deep learning models, to accurately recognize and transcribe text from images of specimen labels. This includes enhancing OCR functionality for Chinese characters and integrating metadata and contextual information to improve accuracy.

C. Checklist for project completion
Provide a bulleted list to the best of your current understanding, of the concrete technical goals and artifacts that, when complete, define the completion of the project. This checklist will likely evolve as your project progresses.
Develop an improved OCR model capable of handling Chinese characters.
Test and validate the OCR model's accuracy on a dataset of pre-1940 plant specimen images.
Incorporate metadata and contextual information into the model to enhance accuracy.
Create clean code and thorough documentation for the project.

D. Outline a path to operationalization.
For this refined project focusing on the improvement of OCR functionality for digitizing natural history specimens, particularly with an emphasis on Chinese characters, and building a public repository, operationalization involves specific technological solutions and collaboration strategies. The project aims to enhance OCR accuracy by incorporating advanced deep learning models such as LSTM-RNN and Transformer models, while also considering the use of metadata and contextual information (e.g., location, collector details) as knowledge priors to improve classification processes. This necessitates a multi-faceted approach involving data gathering from specified sources, model refinement, and the creation of a publicly accessible repository for disseminating the results.
To make the project's outcomes accessible and usable beyond a Jupyter notebook or initial proof of concept, a web-based platform or API could be developed, allowing researchers and the public to upload herbarium images for OCR processing. This platform could be hosted on cloud services like AWS, Google Cloud, or Azure, providing scalable resources for processing and storage. GitHub will serve as the repository for both the codebase and the dataset, facilitating collaboration and open-source contributions. Technologies like Docker could be employed to containerize the application, ensuring ease of deployment and compatibility across different environments. Additionally, integrating the project's outputs into existing databases or platforms frequented by climate change scientists and biodiversity researchers, such as the GBIF, could further extend its impact and utility.


## Resources
### Data Sets
CNH Portal: https://portal.neherbaria.org/portal/

Pre-1940 plant specimen images in GBIF: https://www.gbif.org/occurrence/gallery?basis_of_record=PRESERVED_SPECIMEN&media_ty[…]axon_key=6&year=1000,1941&advanced=1&occurrence_status=present

International Plant Names Index: https://www.gbif.org/dataset/046bbc50-cae2-47ff-aa43-729fbf53f7c5#dataDescription

Use for synonyms (GBIF is recommended): GBIF: https://hosted-datasets.gbif.org/datasets/backbone/current/ 

IPNI: https://storage.cloud.google.com/ipni-data/

CVIT: https://cvit.iiit.ac.in/research/projects/cvit-projects/matchdocimgs

IAM: https://fki.tic.heia-fr.ch/databases/iam-handwriting-database

### References
CRAFT (text detection): https://arxiv.org/abs/1904.01941

TrOCR: https://arxiv.org/abs/2109.10282

"What Is Wrong With Scene Text Recognition Model Comparisons? Dataset and Model Analysis," 10.1109/ICCV.2019.00481

Kubeflow: https://www.kubeflow.org/docs/

Hugging Face Spaces: https://huggingface.co/docs/hub/spaces

GCP Vertex AI: https://cloud.google.com/vertex-ai/docs

AWS SageMaker: https://docs.aws.amazon.com/sagemaker/index.html

TensorFlow Serving: https://github.com/tensorflow/serving

TorchServe: https://github.com/pytorch/serve

# Weekly Meeting Updates

Keep track of ongoing meetings in the Project Description document prepared by Spark staff for your project.
Note: Once this markdown is finalized and merge, the contents of this should also be appended to the Project Description document.

## Temp Link
https://docs.google.com/document/d/1AkQW9WFcBbHqGl8Js3KIth1u3vtOKAgWTyO3nsYgzYI/edit?usp=sharing
Will update to github repo at the end of semester.
