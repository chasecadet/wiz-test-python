FROM python:3.10-slim

# Install curl and yq
RUN apt-get update && \
    apt-get install -y curl && \
    curl -L https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -o /usr/bin/yq && \
    chmod +x /usr/bin/yq && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
# Optional: Copy script directly if you're baking it in
# COPY update.py /app/update.py
ENTRYPOINT ["/bin/bash"]