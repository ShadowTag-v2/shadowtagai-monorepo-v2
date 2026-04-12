FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency definition
COPY pyproject.toml .

# Install dependencies
RUN uv pip install --system -r pyproject.toml

# Copy source code
COPY src/ ./src/

# Set Python path
ENV PYTHONPATH=/app

# Default entrypoint
CMD ["python", "-m", "src.loop"]
