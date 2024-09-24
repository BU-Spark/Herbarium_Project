import pandas as pd
from google.api_core.client_options import ClientOptions
from google.cloud import documentai_v1 as documentai
from google.cloud.documentai_v1.types import RawDocument
import zipfile
import os
import gradio as gr
import tempfile
import textwrap
import json
import google.generativeai as genai
from IPython.display import Markdown
import random
import re
from time import sleep

# —————————————
#     SETUP
# —————————————

# CREDENTIALS FILE PATH
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "herbaria-ai-3c860bcb0f44.json"

# GEMINI API KEY
api_key = os.getenv("API_KEY")
genai.configure(api_key=api_key)

# GEMINI MODEL DECLARATION
model = genai.GenerativeModel('gemini-1.0-pro')

# DOCUMENT AI DETAILS
project_id = "herbaria-ai"
location = "us"
processor_id = "de954414712822b3"

# helper function for processing gemini responses (which are in markdown)
def to_markdown(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

# few-shot samples
shots = \
{
    "Chinese National Herbarium (PE) Plants of Xizang CHINA, Xizang, Lhoka City, Lhozhag County, Lhakang Town, Kharchhu Gompa vicinity 西藏自治区山南市洛扎县拉康镇卡久寺附近 28°5'37.15N, 91°7'24.74″E; 3934 m Herbs. Slopes near roadsides. PE-Xizang Expedition #PE6657 14 September 2017 M4 5 6 7 8 NCIL 中国数字植物标本馆 N° 2604988 西藏 TIBET 中国科学院 植物研究所 标本馆 PE CHINESE NATIONAL HERBARIUM (PE) 02334122 #PE6657 ASTERACEAE 菊科 Anaphalis contorta (D. Don) Hook. f. 鉴定人:张国进 Guo-Jin ZHANG 旋叶香青 17 May 2018"
    :{"Collector":"Guo-Jin, Zhang",
      "Location":"Xizang Autonomous Region, Shannan City, Lhozhag County, Lhakang Town, Kharchhu Gompa vincinity, Slopes near roadsides",
      "Taxon":"Asteraceae; Anaphalis contorta (D. Don) Hook. f.",
      "Date":"14 September 2017",
      "Confidence":".94"
    },

    "PE-Xizang Expedition #PE6673 9 NSIT Chinese National Herbarium (PE) Plants of Xizang CHINA, Xizang, Lhoka City, Lhozhag County, Lhakang Town, Kharchhu Gompa vicinity 28°5&#39;37.15&quot;N, 91°7&#39;24.74&quot;E; 3934 m Herbs. Slopes near roadsides. PE-Xizang Expedition #PE6673 9 NSIT Chinese National Herbarium (PE) Plants of Xizang CHINA, Xizang, Lhoka City, Lhozhag County, Lhakang Town, Kharchhu Gompa vicinity 28°5&#39;37.15&quot;N, 91°7&#39;24.74&quot;E; 3934 m Herbs. Slopes near roadsides. PE-Xizang Expedition #PE6673 9 NSIT Chinese National Herbarium (PE) Plants of Xizang Spiral Leaf Green 17 May 2018"
    :{"Collector":"PE-Xizang Expedition #PE6673",
      "Location":"Xizang Autonomous Region, Lhoka City, Lhozhag County, Lhakang Town, Kharchhu Gompa vicinity, Slopes near roadsides",
      "Taxon":"Spiral Leaf Green",
      "Date":"17 May 2018",
      "Confidence":".76"
    },

    "Honey Plants Research Institute of the Chinese Academy of Agricultural Sciences Collection No.: 13687. May 7, 1993 Habitat Roadside Altitude: 1600 * Characters Shrub No. Herbarium of the Institute of Botany, Chinese Academy of Sciences Collector 3687 Scientific Name Height: m (cm) Diameter at breast height m (cm) Flower: White Fruit: Notes Blooming period: from January to July Honey: Scientific Name: Rosa Sericea Lindl. Appendix: Collector: cm 1 2 3 4 25 CHINESE NATIONAL HERBARUM ( 01833954 No 1479566 * Herbarium of the Institute of Botany, Chinese Academy of Sciences Sichuan SZECHUAN DET. Rosa sercea Lindl. var. Various Zhi 2009-02-16"
    :{"Collector":"UNKNOWN",
      "Location":"Sichuan, China, Roadside, Altitude: 1600",
      "Taxon":"Rosa sericea",
      "Date":"7 May 1993",
      "Confidence":".45"
    },
}

# ————————————
#     FUNC
# ————————————

# few-shot randomizer
def get_random_pairs_list(input_dict, num_pairs=3):
    if len(input_dict) < num_pairs:
        return "Not enough elements in the dictionary to select the requested number of pairs"
    keys = random.sample(list(input_dict.keys()), num_pairs)
    return [(key, input_dict[key]) for key in keys]

# main gemini processor
def generate_metadata(results_df, shots):
    responses = []
    for input_text in results_df["extracted_text"]:

        # FEW-SHOT RANDOMIZER
        random_pairs = get_random_pairs_list(shots)

        # PROMPT FORMATTING
        prompt = \
        """
        Your goal is to translate (if necessary) and then extract four items from a
        string of text: the name of the specimen collector, the location, the taxon
        and/or any identifying information about the specimen, and the earliest date.
        Your response should contain only JSON. Use the best information available
        or insert 'UNKNOWN' if there is none. Provide a rough estimate of confidence
        in your output ranging from 0-1 inside your JSON output.

        Examples:

        Input 1:
        {shot1_input}
        Output 1:
        {{"Collector":"{shot1_output_collector}","Location":"{shot1_output_location}","Taxon":"{shot1_output_taxon}","Date":"{shot1_output_date}","Confidence":"{shot1_confidence}"}}

        Input 2:
        {shot2_input}
        Output 2:
        {{"Collector":"{shot2_output_collector}","Location":"{shot2_output_location}","Taxon":"{shot2_output_taxon}","Date":"{shot2_output_date},"Confidence":"{shot2_confidence}"}}

        Input 3:
        {shot3_input}
        Output 3:
        {{"Collector":"{shot3_output_collector}","Location":"{shot3_output_location}","Taxon":"{shot3_output_taxon}","Date":"{shot3_output_date},"Confidence":"{shot3_confidence}"}}

        Your attempt:
        Input:
        {input_text}
        Output:

        """.format(
        shot1_input = random_pairs[0][0],
        shot1_output_collector = random_pairs[0][1]['Collector'],
        shot1_output_location = random_pairs[0][1]['Location'],
        shot1_output_taxon = random_pairs[0][1]['Taxon'],
        shot1_output_date = random_pairs[0][1]['Date'],
        shot1_confidence = random_pairs[0][1]['Confidence'],

        shot2_input = random_pairs[1][0],
        shot2_output_collector = random_pairs[1][1]['Collector'],
        shot2_output_location = random_pairs[1][1]['Location'],
        shot2_output_taxon = random_pairs[1][1]['Taxon'],
        shot2_output_date = random_pairs[1][1]['Date'],
        shot2_confidence = random_pairs[1][1]['Confidence'],

        shot3_input = random_pairs[2][0],
        shot3_output_collector = random_pairs[2][1]['Collector'],
        shot3_output_location = random_pairs[2][1]['Location'],
        shot3_output_taxon = random_pairs[2][1]['Taxon'],
        shot3_output_date = random_pairs[2][1]['Date'],
        shot3_confidence = random_pairs[2][1]['Confidence'],

        input_text = input_text
        )

        response = model.generate_content(prompt)
        responses.append(response)

    return responses

# gemini response handler
def process_responses(responses):
    text_responses = []
    for response in responses:
        extracted_text = to_markdown(response.text).data
        text_responses.append(extracted_text.strip().replace('>', '')[1:])

    json_responses = []
    for text in text_responses:
        try:
            json_response = json.loads(re.search(r'{.*}', text, re.DOTALL).group())
            json_responses.append(json_response)
        except json.JSONDecodeError as e:
            print("Failed on input", text_responses.index(text), "| Reason:", e)
            continue

    return json_responses

# main document AI processor
def batch_process_documents(file_path: str, file_mime_type: str) -> tuple:
    opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
    client = documentai.DocumentProcessorServiceClient(client_options=opts)

    with open(file_path, "rb") as file_stream:
        raw_document = RawDocument(content=file_stream.read(), mime_type=file_mime_type)

    name = client.processor_path(project_id, location, processor_id)
    request = documentai.ProcessRequest(name=name, raw_document=raw_document)
    result = client.process_document(request=request)

    extracted_text = result.document.text.replace('\n', ' ')
    return extracted_text

# file upload
def unzip_and_find_jpgs(file_path):
    extract_path = "extracted_files"
    if os.path.exists(extract_path):
        # clear dir
        for root, dirs, files in os.walk(extract_path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(extract_path)

    os.makedirs(extract_path, exist_ok=True)
    jpg_files = []
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
        for root, dirs, files in os.walk(extract_path):
            if '__MACOSX' in root:
                continue
            for file in files:
                if file.lower().endswith('.jpg'):
                    full_path = os.path.join(root, file)
                    jpg_files.append(full_path)
    return jpg_files

# ————————————
#     MAIN
# ————————————

def process_images(uploaded_file):
    # make new dataframe each time this function is called
    results_df = pd.DataFrame(columns=["filename", "collector", "location", "taxon", "date", "confidence", "extracted_text"]) 

    # easy gradio filename storage
    file_path = uploaded_file.name

    try:
        image_files = unzip_and_find_jpgs(file_path)

        if not image_files:
            return "No JPG files found in the zip."
        
        print(image_files)

        for file_path in image_files:
            # DOCUMENT AI PROCESSING IS HERE
            extracted_text = batch_process_documents(file_path, "image/jpeg")
            new_row = pd.DataFrame([{
                "filename": os.path.basename(file_path),
                "extracted_text": extracted_text
            }])
            results_df = pd.concat([results_df, new_row], ignore_index=True)

        # GEMINI PROCESSING IS HERE
        responses = generate_metadata(results_df, shots)
        processed_data = process_responses(responses)

        # append extracted metadata
        for idx, processed in enumerate(processed_data):
            results_df.at[idx, "collector"] = processed.get("Collector", "")
            results_df.at[idx, "location"] = processed.get("Location", "")
            results_df.at[idx, "taxon"] = processed.get("Taxon", "")
            results_df.at[idx, "date"] = processed.get("Date", "")
            results_df.at[idx, "confidence"] = processed.get("Confidence", "")

    except Exception as e:
        return f"An error occurred: {str(e)} on file {file_path}"

    html_output = results_df.to_html()

    # CSV saving (with temp file)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    results_df.to_csv(temp_file.name, index=False)

    temp_file.close()

    # return HTML and output CSV path
    return html_output, temp_file.name

# ———————————
#     UI
# ———————————

with gr.Blocks() as interface:
    with gr.Row():
        gr.Markdown("# Herbaria Batch Metadata Extraction")
        gr.Markdown("Upload a ZIP file containing JPEG/JPG images, and the system will translate and extract the text from each image.")
    with gr.Row():
        file_input = gr.File(label="Upload ZIP File")
    with gr.Row():
        html_output = gr.HTML(label="Extracted Text From Your Herbaria Images")
    with gr.Row():
        file_output = gr.File(label="Download this file to receive the extracted labels from the images.")

    file_input.change(process_images, inputs=file_input, outputs=[html_output, file_output])

if __name__ == "__main__":
    interface.launch(debug=True)