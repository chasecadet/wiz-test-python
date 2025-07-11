# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Install dependencies (git, yq, and other utilities)
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    # Install yq (YAML processor)
    && curl -sL https://github.com/mikefarah/yq/releases/download/v4.15.1/yq_linux_amd64 -o /usr/local/bin/yq \
    && chmod +x /usr/local/bin/yq

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python script into the container
COPY promote_image.py .

# Set environment variables (optional if you want to pass these at runtime)
ENV GITHUB_TOKEN=""
ENV GITHUB_USERNAME=""
ENV REPO_URL=""
ENV NEW_IMAGE=""
ENV GITHUB_REPO=""

# Run the script by default
ENTRYPOINT ["python", "promote_image.py"]
