FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    xmlsec1 \
    libxmlsec1-dev \
    pkg-config \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "sp_app.py"]