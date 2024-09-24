# Herbaria Batch Metadata Extraction

Welcome to the Herbaria Batch Metadata Extraction web app, hosted on HuggingFace Spaces! This app allows users to upload a ZIP file containing JPEG images of herbarium specimens. The system leverages advanced AI to translate text within the images and extract key metadata, including the collector's name, location, taxon, and date of collection.

## Features

- **Batch Processing**: Upload a ZIP file and process multiple images simultaneously.
- **Advanced AI Models**: Utilizes Google's Document AI for text extraction and the Gemini generative model for metadata interpretation.
- **High Accuracy**: Incorporates few-shot learning examples to improve the accuracy of metadata extraction.
- **User-Friendly Interface**: Easy to use web interface built with Gradio.

## How to Use

1. **Access the App**: Navigate to the [Herbaria Batch Metadata Extraction](<https://huggingface.co/spaces/spark-ds549/TrOCR>) on HuggingFace Spaces.
2. **Upload Your File**: Click on "Upload ZIP File" and select a ZIP file containing JPEG images.
3. **View Results**: The extracted metadata will be displayed on the web page.
4. **Download Results**: Click on "Download this file" to save the extracted labels as a CSV file.

## Setup and Configuration

### Prerequisites
- Google Cloud account with access to Document AI.
- API key for the Gemini model.

### Environment Variables
- Currently both environment variables are set for initial testing and usage of the application.
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to your Google Cloud credentials file.
- `API_KEY`: Your API key for the Gemini model.

## Future Enhancements

- **API Key Configuration**: For broader distribution, future versions may require users to provide their own API keys.
- **Usage Billing**: Depending on the deployment scale and usage, a billing system may be introduced to cover operational costs.

## Contributing

We welcome contributions from the community, including bug fixes, improvements, or feature requests. Please feel free to fork the repository and submit a pull request.

## Acknowledgements

- Google Cloud for Document AI services.
- HuggingFace for hosting the web app on Spaces.
