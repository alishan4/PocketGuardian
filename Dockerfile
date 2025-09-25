FROM continuumio/anaconda3

WORKDIR /app

COPY environment.yml .
RUN conda env create -f environment.yml

COPY . /app

ENV PATH /opt/conda/envs/pocketguardian/bin:$PATH

CMD ["python", "backend/app.py"]