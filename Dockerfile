FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim

RUN groupadd -r mcp && useradd -r -g mcp mcp

# Install runtime dependencies (kubectl, helm, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    dnsutils \
    openssl \
    && rm -rf /var/lib/apt/lists/*

# Install kubectl
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    && install kubectl /usr/local/bin/ && rm kubectl

# Install helm
RUN curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

WORKDIR /app

COPY --from=builder /install /usr/local
COPY src/ ./src/
COPY pyproject.toml .

USER mcp

HEALTHCHECK --interval=30s --timeout=3s \
    CMD python -c "import src.config; print('ok')" || exit 1

ENTRYPOINT ["python", "-m", "src.server"]
