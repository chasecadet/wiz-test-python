FROM python:3.10-slim

# Install pyyaml for Python YAML manipulation
RUN pip install --no-cache-dir pyyaml

WORKDIR /app

ENTRYPOINT ["/bin/bash"]
