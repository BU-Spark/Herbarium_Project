# Random utility functions
from PIL import Image
import os
import random
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset


# Create a CVIT dataset class  
class CVITDataset(Dataset):
    def __init__(self, df, processor, max_target_length=128):
        self.df = df
        self.processor = processor
        self.max_target_length = max_target_length

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        # get file name + text 
        image = self.df['image'][idx]
        text = self.df['label'][idx]
        # prepare image (i.e. resize + normalize)
        image = Image.open(image).convert("RGB")
        pixel_values = self.processor(image, return_tensors="pt").pixel_values
        # add labels (input_ids) by encoding the text
        labels = self.processor.tokenizer(text, 
                                          padding="max_length", 
                                          max_length=self.max_target_length).input_ids
        # important: make sure that PAD tokens are ignored by the loss function
        labels = [label if label != self.processor.tokenizer.pad_token_id else -100 for label in labels]

        encoding = {"pixel_values": pixel_values.squeeze(), "labels": torch.tensor(labels)}
        return encoding
        

def create_CVIT(df,processor):
    """
    Given a dataframe and a processor, this function creates a training and validation dataset for the CVIT dataset.
    
    Parameters:
    df (pandas.DataFrame): A DataFrame containing the data to split into training and validation sets.
    processor (callable): A callable object that processes the data from the DataFrame.
    
    Returns:
    tuple: A tuple containing the training and validation datasets as instances of the CVITDataset class.
    """
    # Training and validaiton splits for CVIT dataset
    train_df, val_df = train_test_split(df, test_size=0.2, random_state=42)
    train_df.reset_index(drop=True, inplace=True)
    val_df.reset_index(drop=True, inplace=True)
    
    train_dataset = CVITDataset(df=train_df,processor=processor)
    val_dataset = CVITDataset(df=val_df,processor=processor)

    return train_dataset,val_dataset

def show_random_CVIT_image(df):
    # Display a random image from the CVIT dataset and its label
    random_image = random.choice(df['image'])
    print('Ground Truth:',df.loc[df['image'] == random_image]['label'].values[0])
    img = Image.open(random_image)
    display(img)


# Total size of directories
def get_size(start_path = '.'):
    # Print out the total size of a directory and its subdirectories
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
        print(total_size)

    return total_size

def catch_invalid(img):
    try:
        a = Image.open(img)
        a.close()
    except Exception as e:
        print(e)
        return False
    return True


def catch_invalid2(img):
    try:
        a = Image.open(img)
        a.close()
    except Exception as e:
        print(e)
        return False,img
    return True

def mb2bytes(mb):
    return mb * 1024 * 1024

def copy_files(src, dest, size):
    # copy files from src to dest until if size of file is above size
    total_moved = 0
    for root, dirs, files in os.walk(src):
        for file in files:
            if os.path.getsize(os.path.join(root, file)) > mb2bytes(size):
#                 print(os.path.join(root, file))
                shutil.copy(os.path.join(root, file), dest)
                total_moved +=1
    print('Copied %d files to %s'%(total_moved,dest))