# Use the official Python image from the Docker Hub
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Install ImageMagick
RUN apt-get update && \
    apt-get install -y imagemagick

# Copy the rest of the application code
COPY . .

# Expose port 80
EXPOSE 80

# Define the command to run the application
CMD ["python", "GenAI.py"]
