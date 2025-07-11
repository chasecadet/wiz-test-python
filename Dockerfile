FROM python:3.13-slim
# Install Git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
# Create working directory
WORKDIR /app
# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copy the main script
COPY promote_image.py .
# Make sure script is executable
RUN chmod +x promote_image.py
# Entrypoint to run script with args
ENTRYPOINT ["python", "promote_image.py"]
