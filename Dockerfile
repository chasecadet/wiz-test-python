FROM python:3.11-slim
RUN pip install --upgrade pip
RUN pip install --no-cache-dir kestra requests pyyaml
