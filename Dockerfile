# Use the official Python image as a base
FROM python:3.12.5-bullseye

# Set environment variables to avoid .pyc files and ensure stdout and stderr are unbuffered
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /usr/src/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    netcat \
    postgresql-client

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the entrypoint script and fix line endings
# COPY entrypoint.sh /usr/src/app/entrypoint.sh
# RUN sed -i 's/\r$//' /usr/src/app/entrypoint.sh
# RUN chmod +x /usr/src/app/entrypoint.sh

# Copy the project files
COPY . /usr/src/app/

# Set the entrypoint
# ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
