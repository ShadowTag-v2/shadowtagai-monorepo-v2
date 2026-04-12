
# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
# We use the root requirements.in as the base
COPY requirements.in /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
# We copy the src directory to /app/src and libs to /app/libs to match pythonpath
COPY src /app/src
COPY libs /app/libs

# Set Python path to include src and libs
ENV PYTHONPATH=/app:/app/src:/app/libs

# Expose the port the app runs on
EXPOSE 8080

# Run the autoresearch server
# Assuming the entrypoint is similar to the main server, or this is a worker.
# Based on main.tf, this is "antigravity-sidecar".
# We'll use a default command that keeps it alive or runs the agent.
# For now, let's run the agent runner script if it exists, or wait.
CMD ["python3", "-m", "src.antigravity.autoresearch"]
