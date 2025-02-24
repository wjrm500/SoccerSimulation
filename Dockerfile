# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the application files into the container
COPY app.py worker.py delete_12_hour_mongodb_data.py pyproject.toml /app/
COPY blueprints /app/blueprints/
COPY frontend /app/frontend/
COPY ss /app/ss/
COPY utils /app/utils/

# Install curl (required for the uv installer), then install uv using its standalone installer.
RUN apt-get update && apt-get install -y curl && \
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    apt-get remove -y curl && apt-get clean && rm -rf /var/lib/apt/lists/*

# Add uv's installation directory to the PATH (it installs uv to /root/.local/bin)
ENV PATH="/root/.local/bin:${PATH}"

# Synchronise dependencies with uv.
# This command creates a virtual environment (by default in .venv) and installs dependencies as specified in pyproject.toml (and uv.lock if available).
RUN uv sync

# Expose port 5000
EXPOSE 5000

# Run the application using uv run, which executes gunicorn within the project's virtual environment
CMD ["uv", "run", "gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
