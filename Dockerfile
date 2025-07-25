FROM python:3.9-slim

WORKDIR /app
COPY . /app

RUN apt-get update && apt-get install -y \
    gcc g++ build-essential poppler-utils \
    libjpeg-dev zlib1g-dev libfreetype6-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Step 1: Install torch first
RUN pip install --no-cache-dir torch==2.0.1+cpu -f https://download.pytorch.org/whl/torch_stable.html

# Step 2: Install compatible versions of the rest
RUN pip install --no-cache-dir \
    transformers==4.30.2 \
    sentence-transformers==2.2.2 \
    huggingface-hub==0.15.1 \
    pdfplumber \
    PyMuPDF \
    numpy \
    scikit-learn \
    pillow \
    requests

CMD ["python", "main_pipeline.py", "--input", "/app/input.json", "--output", "/app/output/output.json"]
