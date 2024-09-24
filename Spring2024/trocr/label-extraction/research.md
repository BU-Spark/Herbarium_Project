# [Research] DETR (DEtection TRansformer)

### Overview
To choose an optimal model for detecting labels in plant sample images, a review of various models was undertaken. The task was to discern labels from plant specimen images, with potential models including LayoutLMv3[^1^] and DETR[^2^]. A detailed comparison and a critical review of the models led to an optimal model selection, aligning with the project's specific goals and constraints.

### Analysis of Models
During the model selection process, **BioBERT**[^3^](as part of the TaxoNERD module - paper[^4^] and GitHub[^5^]) and **LayoutLMv3** were meticulously analyzed, with the former already in use in our post-OCR step.

- **BioBERT:**
  The BioBERT paper emphasizes the significance of pre-training with biomedical text. The model, trained over 23 days utilizing 8 V100 GPUs, exhibited superior performance over pre-trained BERT in scientific Named Entity Recognition (NER) tasks.

- **LayoutLMv3:**
  LayoutLMv3 initialized its text modality with RoBERTa weights and underwent subsequent pre-training on the IIT-CDIP dataset[^6^]. The multi-model nature of the model could prove effective as well.

An in-depth reading of these papers raised concerns over the loss of nuanced information learned from pre-training on medical text, which could potentially be a setback for the project. The risk was highlighted by our objective to focus information extraction solely from the labels on our specimen images, and implementing LayoutLMv3 could potentially deviate us from this goal.

### Rationale for Model Selection
Given the potential limitations and changes required to the existing pipeline, to have BioBERT as an isolated post-processing step was preferred. This would offer flexibility in integrating later models like **SciBERT**[^7^] and leveraging off-the-shelf models pre-trained on biomedical text. 

With the constrained timeline, aiming to label adequate data, pre-training the text modality of the LayoutLMv3 model, and documenting the results appeared ambitious. 

Therefore, given the considerations and project alignment, DETR was opted for as the preferred model to detect labels in our specimen images. DETR’s proficiency in detecting objects, in our case labels (which are in essence, rectangular shapes) made it a fitting choice, as it synchronized well with our usecase. Additionally, integrating LayoutLMv3 would have necessitated considerable modifications to the existing pipeline, risking the loss of advantages gained from the pre-trained BioBERT.

The model's availability on Hugging Face is also a major factor in terms of codebase maintainability and has made it an optimal choice for our task. Please feel free to checkout other models for object detection on "Papers with code".

### About DETR

DETR leverages the transformer architecture, predominantly used for NLP tasks, to process image data effectively, making it stand out from traditional CNN-based detection models. It fundamentally alters the conventional object detection paradigms, removing the need for anchor boxes and employing a bipartite matching loss to handle objects of different scales and aspect ratios, thereby mitigating issues prevalent in region proposal-based methods. The model enables processing both convolutional features and positional encodings concurrently, optimizing spatial understanding within images.

On benchmark datasets like COCO[^8^], DETR exhibits better performance, demonstrating its ability to optimize the Intersection over Union (IoU) metric, while maintaining high recall rates. It uses a set-based global loss, which helps in overcoming issues related to occlusion and object density, establishing a higher benchmark for complex tasks.

Its application has extended to medical image analysis, where precise detection is pivotal. It has been especially impactful in instances where identifying and localizing multiple objects within images is crucial, such as in surveillance and autonomous vehicle navigation.

---

### Evaluation Summary

The model's performance was evaluated using the COCO evaluation metrics, a standard benchmark for object detection algorithms. The following results provide insights into its accuracy and precision:

- **Intersection over Union (IoU)**: 
  - This metric quantifies the overlap between the predicted bounding box and the actual ground truth. Higher values indicate better alignment between predictions and ground truth.
  
- **Average Precision (AP)**:
  - `AP (IoU=0.50:0.95, all sizes)`: 0.229
    - A comprehensive metric measuring the model's precision over multiple IoU thresholds (0.50 to 0.95) and object sizes.
  - `AP (IoU=0.50, all sizes)`: 0.401
    - At a lenient overlap requirement of 0.50, the model exhibits a precision of 0.401.
  - `AP (IoU=0.75, all sizes)`: 0.262
    - At a stricter overlap of 0.75, precision drops slightly.
  - For specific object sizes:
    - `AP (IoU=0.50:0.95, large objects)`: 0.229
    - The model's precision for small and medium objects was not evaluated or not available in the dataset.

- **Average Recall (AR)**:
  - Reflecting the model's ability to identify all potential objects:
    - `AR (maxDets=1)`: 0.161
    - `AR (maxDets=10)`: 0.316
    - `AR (maxDets=100)`: 0.316
  - For specific object sizes:
    - `AR (IoU=0.50:0.95, large objects)`: 0.316
    - Recall for small and medium objects was not evaluated or not available in the dataset.

**Interpretation**: 
The model demonstrates respectable precision, especially at a lenient IoU threshold of 0.50. While precision tends to drop with stricter IoU thresholds, the average recall indicates the model's consistent ability to identify objects, especially when considering a larger number of detections per image. The model's proficiency in detecting larger objects is evident, while its performance on smaller or medium objects requires further assessment and improvement.

---

### References:

[^1^]: [LayoutLMv3](https://arxiv.org/abs/2204.08387).
[^2^]: [DETR (DEtection TRansformer)](https://arxiv.org/abs/2005.12872)
[^3^]: [BioBERT](https://arxiv.org/abs/1901.08746)
[^7^]: [SciBERT](https://arxiv.org/abs/1903.10676)
[^4^]: [TaxoNERD](https://besjournals.onlinelibrary.wiley.com/doi/10.1111/2041-210X.13778).
[^6^]: [IIT-CDIP Dataset](https://data.nist.gov/od/id/mds2-2531).
[^8^]: [COCO Dataset](http://cocodataset.org/).
[^5^]: [TaxoNERD GitHub Repository](https://github.com/nleguillarme/taxonerd).
