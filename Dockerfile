# ---------- Stage 1: Builder ----------
FROM python:3.11-slim-bookworm AS builder
# COPY --from=ghcr.io/astral-sh/uv:0.7.3 /uv /uvx /bin/

# Prepare working directory
WORKDIR /app

RUN apt-get update \
    && apt-get install -y poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
ENV UV_SYSTEM_PYTHON=1
# Copy the rest of the code
COPY src/ ./src/
COPY pyproject.toml .
RUN --mount=from=ghcr.io/astral-sh/uv:0.7.3,source=/uv,target=/bin/uv uv pip install --system --no-cache-dir -e .

#RUN uv pip install --system --no-cache-dir -e .

COPY ui.py ./
COPY example.env .env

# Expose Streamlit default port
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "ui.py", "--server.port=8501", "--server.address=0.0.0.0"]
