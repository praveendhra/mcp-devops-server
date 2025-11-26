FROM python:3.12-slim

WORKDIR /app

# Install system dependencies (kubectl, awscli, gh)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    && install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl \
    && rm kubectl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

COPY . .

RUN useradd -r -s /bin/false mcpuser
USER mcpuser

ENTRYPOINT ["python", "-m", "mcp_devops_server"]
