FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Application Code
# We copy src/ and libs/ to ensure the import structure matches local dev
COPY src/ ./src/
COPY libs/ ./libs/

# Create empty directories if missing (for safety)
RUN mkdir -p Docs scripts tests

# Expose Port (Cloud Run Default)
ENV PORT=8080
EXPOSE 8080

# Run the MCP Server (Core Brain)
# We use the relative path as defined in mcp_server.py
CMD ["python", "src/governance/mcp_server.py"]
