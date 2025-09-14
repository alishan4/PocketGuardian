# Use Anaconda base image
FROM continuumio/anaconda3:latest

# Set working directory
WORKDIR /app
COPY . .

# Create Conda environment
RUN conda env create -f environment.yml

# Use conda shell
SHELL ["conda", "run", "-n", "pocketguardian", "/bin/bash", "-c"]

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Expose Flask port
EXPOSE 5000

# Run Flask app
CMD ["conda", "run", "-n", "pocketguardian", "python", "backend/app.py"]