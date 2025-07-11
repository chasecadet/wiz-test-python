FROM python:3.13-slim
# Add system dependencies needed to build Python wheels

# Install system dependencies needed to build Python wheels
RUN apt-get update && apt-get install -y \
    gcc \
    libyaml-dev \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
WORKDIR /app
# Install Python dependencies
COPY promote_image.py .
# Make sure script is executable
RUN chmod +x promote_image.py
# Entrypoint to run script with args
ENTRYPOINT ["python", "promote_image.py"]
