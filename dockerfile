# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for mysqlclient and other Python packages
RUN apt-get update && \
    apt-get install -y \
    python3-dev \
    pkg-config \
    default-libmysqlclient-dev \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port your Flask app runs on
EXPOSE 5000

# Define the command to run your app
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]

