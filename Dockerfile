# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY app.py requirements.txt worker.py delete_12_hour_mongodb_data.py /app/
COPY frontend /app/frontend/
COPY ss /app/ss/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
