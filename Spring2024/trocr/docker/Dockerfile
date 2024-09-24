# Use an official Miniconda3 as a parent image
FROM continuumio/miniconda3:latest

# Set the working directory in docker
WORKDIR /usr/src/app

# Declare argument for conda environment name
ARG CONDA_ENV_NAME=trocr_env

# Clone the repository
RUN git clone https://github.com/BU-Spark/ml-herbarium.git . && \
    git checkout dev && \
    cd trocr

# Create a new conda environment from the YAML file and activate it
RUN conda env create -n $CONDA_ENV_NAME --file=trocr_env.yml && \
    echo "conda activate $CONDA_ENV_NAME" >> ~/.bashrc

# Install Jupyter and other required packages
RUN conda install -n $CONDA_ENV_NAME jupyter -y && \
    /opt/conda/envs/$CONDA_ENV_NAME/bin/pip install transformers==4.27.0 --no-deps && \
    /opt/conda/envs/$CONDA_ENV_NAME/bin/pip install https://github.com/nleguillarme/taxonerd/releases/download/v1.5.0/en_core_eco_md-1.0.2.tar.gz && \
    /opt/conda/envs/$CONDA_ENV_NAME/bin/pip install https://github.com/nleguillarme/taxonerd/releases/download/v1.5.0/en_core_eco_biobert-1.0.2.tar.gz && \
    /opt/conda/envs/$CONDA_ENV_NAME/bin/python -m spacy download en_core_web_sm && \
    /opt/conda/envs/$CONDA_ENV_NAME/bin/python -m spacy download en_core_web_md && \
    /opt/conda/envs/$CONDA_ENV_NAME/bin/python -m spacy download en_core_web_trf
    
# Make port 8888 available to the world outside this container
EXPOSE 8888

# Run Jupyter Notebook when the container launches
CMD [ "/opt/conda/envs/$CONDA_ENV_NAME/bin/jupyter", "notebook", "--ip='*'", "--port=8888", "--no-browser", "--allow-root" ]
