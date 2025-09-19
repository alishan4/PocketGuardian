FROM continuumio/anaconda3:latest

WORKDIR /app

COPY . .

# Create Conda environment
RUN conda env create -f environment.yml

# Use conda shell
SHELL ["conda", "run", "-n", "pocketguardian", "/bin/bash", "-c"]

# Install spaCy model
RUN python -m spacy download en_core_web_sm

# Expose ports for Flask (5000) and Streamlit (8501)
EXPOSE 5000 8501

# Start both Flask and Streamlit
CMD ["bash", "-c", "conda run -n pocketguardian python backend/app.py & conda run -n pocketguardian streamlit run frontend/app.py --server.port 8501"]