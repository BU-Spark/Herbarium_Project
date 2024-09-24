import torch
from tqdm import tqdm
import numpy as np
import pandas as pd
import torch.nn.functional as F
# All functions associated with the trocr transcription of the model

# Yoinked https://github.com/rsommerfeld/trocr/blob/main/src/scripts.py
# Used for calculating the model confidene in transcriptoins
def get_confidence_scores(generated_ids):
    """
    Given logits, return the confidence scores
    
    Parameters:
    generated_ids (torch.Tensor): Logits from the model
    
    Returns:
    list: List of confidence scores
    """
    # Takes in the output of the model and returns the confidence scores

    # Get raw logits, with shape (examples,tokens,token_vals)
    logits = generated_ids.scores
    logits = torch.stack(list(logits),dim=1)

    # Transform logits to softmax and keep only the highest (chosen) p for each token
    logit_probs = F.softmax(logits, dim=2)
    char_probs = logit_probs.max(dim=2)[0]

    # Only tokens of val>2 should influence the confidence. Thus, set probabilities to 1 for tokens 0-2
    mask = generated_ids.sequences[:,:-1] > 2
    char_probs[mask] = 1

    # Confidence of each example is cumulative product of token probs
    batch_confidence_scores = char_probs.cumprod(dim=1)[:, -1]
    return [v.item() for v in batch_confidence_scores]

def evaluate_craft_seg(model,processor,words_identified,word_log_dic,testloader,device):
    """
    Given a model, processor, words identified, word log dictionary, testloader, and device, evaluate the model on the CRAFTed segmentations
    
    Parameters:
    model (torch.nn.Module): The model to evaluate
    processor (torch.nn.Module): The processor to use
    words_identified (list): List of words to identified
    word_log_dic (dict): Dictionary of image and label associations
    testloader (torch.utils.data.DataLoader): The testloader to use
    device (torch.device): The device to use
    
    Returns:
    pandas.DataFrame: results of the evaluation, including the transcription, confidence, and label
    """
    # Takes in a model, processor, words identified, word log dictionary, testloader, and device, and 
    # returns the associated transcriptions, transcription confidence, and image label
    results = []
    confidence = []
    label = []

    # Training loop
    model.eval()
    if device == 'cuda':
        with torch.no_grad():
            for idx,data in enumerate(tqdm(testloader,desc='Transcribing Image Segments')):

                images, labels = data
                images, labels = images['pixel_values'][0].to(device), labels.to(device)
                
                decoded = model.module.generate(images,return_dict_in_generate = True, output_scores = True) 
        
                final_values = processor.batch_decode(decoded.sequences, skip_special_tokens=True)
                
                confidences = get_confidence_scores(decoded)

                for idx,value in enumerate(labels.cpu().numpy()):
                    words_identified[word_log_dic[value]].append(final_values[idx])
                
                results.extend(final_values)
                confidence.extend(confidences)
                label.extend(labels.cpu().numpy())
    else:
        with torch.no_grad():
            for idx,data in enumerate(tqdm(testloader,desc='Transcribing Image Segments')):

                images, labels = data
                images, labels = images['pixel_values'][0].to(device), labels.to(device)
                
                decoded = model.generate(images,return_dict_in_generate = True, output_scores = True) 
        
                final_values = processor.batch_decode(decoded.sequences, skip_special_tokens=True)
                
                confidences = get_confidence_scores(decoded)

                for idx,value in enumerate(labels.cpu().numpy()):
                    words_identified[word_log_dic[value]].append(final_values[idx])
                
                results.extend(final_values)
                confidence.extend(confidences)
                label.extend(labels.cpu().numpy())

    return results,confidence,label

def combine_by_label(df):
    """
    Given a dataframe, combine the transcriptions and confidence scores by label
    
    Parameters:
    df (pd.DataFrame): Dataframe with columns 'Results' and 'Confidence'
    
    Returns:
    pandas.DataFrame: A DataFrame containing the combined transcriptions and confidence scores
    """
    # Combines the transcriptions and confidences by label

    ukeys, index = np.unique(df.Labels, True)
    conf = np.split(df.Confidence, index[1:])
    text = np.split(df.Results, index[1:])

    df2 = pd.DataFrame({'Labels':ukeys, 'Transcription':[list(a) for a in text],'Transcription_Confidence':[list(a) for a in conf]})
    return df2