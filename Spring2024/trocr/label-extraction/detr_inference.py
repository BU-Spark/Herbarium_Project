import logging
import os

import torch

import numpy as np
from PIL import Image, ImageDraw
from transformers import (
    DetrImageProcessor,
    DetrForObjectDetection,
    Pipeline,
    pipeline,
)

import click

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("detr-object-detection")


def run_object_detection_pipeline(pipe: Pipeline, image: Image) -> Image:
    bounding_boxes = []
    for results in pipe(image):
        bbox = results["box"]
        item = results["label"]
        score = round(results["score"], 3)

        # let's only keep detections with score > 0.9
        if score > 0.0:
            bounding_boxes.append(bbox)
            
    logging.info("Masking image...")
    masked_image = mask_image(image, bounding_boxes)
    
    return masked_image


def mask_image(image: Image, bounding_boxes: list) -> Image:
    """
    Sets all pixels outside the bounding boxes to white (255, 255, 255).
    
    Parameters:
    - image (PIL.Image): The source image.
    - bounding_boxes (list): A list of bounding box dictionaries. Each bounding box is expected to be 
      in the format: {'xmin': xmin, 'ymin': ymin, 'xmax': xmax, 'ymax': ymax}
    
    Returns:
    - PIL.Image: The modified image.
    """
    
    # Create a black mask of the same size as the image
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)
    
    # Draw filled rectangles (in white) on the mask for each bounding box
    for bbox in bounding_boxes:
        (xmin, ymin, xmax, ymax) = (
            bbox["xmin"],
            bbox["ymin"],
            bbox["xmax"],
            bbox["ymax"],
        )
        draw.rectangle([xmin, ymin, xmax, ymax], fill=255)
    
    # Use the mask to blend the original image and a white image
    white_image = Image.new('RGB', image.size, (255, 255, 255))
    masked_image = Image.composite(image, white_image, mask)
    
    return masked_image


@click.command()
@click.option(
    "--image-folder",
    help="Folder with input images",
    required=True
)
@click.option(
    "--pretrained-model",
    help="Name of the model on Hugging Face",
    default="spark-ds549/detr-label-detection"
)
@click.option(
    "--output-folder",
    help="Folder to store DETR output images. The image pixels are masked outside the bounding boxes.",
    required=True
)
@click.option(
    "--cache-dir",
    help="Folder to cache models. It is recommended to provide one. Default is the 'data' directory in the project folder",
    default="data/"
)
def run(image_folder: str, pretrained_model: str, output_folder: str, cache_dir: str):
    """
    CLI program that pulls a pretrained DETR model from huggingface, and runs it
    on an image passed via a URL. The results are then saved to a file.

    Default model: spark-ds549/detr-label-detection

    Default filename: detr-bounding-boxes.png
    """

    logger.info(f"Getting {pretrained_model} pretrained model...")

    # Moving model to GPU
    if(torch.cuda.is_available()):
        model = DetrForObjectDetection.from_pretrained(pretrained_model, cache_dir=cache_dir).to('cuda')
        device = 0 # if GPU is available
    else:
        model = DetrForObjectDetection.from_pretrained(pretrained_model, cache_dir=cache_dir) 
        device = -1 # if GPU is unavailable
    processor = DetrImageProcessor.from_pretrained(pretrained_model, cache_dir=cache_dir)

    logger.info("Setting up object detection pipeline...")
    pipe = pipeline(
        "object-detection", model=model, feature_extractor=processor, device=device
    )

    logger.info("Running object detection pipeline...")

    label_bboxes = {}
    
    for file in os.listdir(image_folder):
        if(file.split(".")[-1] not in ["jpg", "png", "jpeg"]):
            continue
        
        image_path = os.path.join(image_folder, file)
    
        logger.info(f"Getting image at path {image_path}...")
    
        # read image from local storage
        image = Image.open(image_path)
        logger.info(f"Now have image object {image}")
    
        masked_image = run_object_detection_pipeline(pipe=pipe, image=image)

        output_file = os.path.join(output_folder, file)
        masked_image.save(output_file)
        logging.info(f"Saved image to location: {output_file}")
        

if __name__ == "__main__":
    run()