# Use the official Python image from the Docker Hub
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Install ImageMagick and FFmpeg
RUN apt-get update && \
    apt-get install -y imagemagick ffmpeg

# Install additional fonts
RUN apt-get install -y fonts-dejavu

# Add folder permission
RUN mkdir -p /app/audio /app/images /app/videos && chmod -R 777 /app

# Copy the updated policy.xml to the container
COPY policy.xml /etc/ImageMagick-6/policy.xml

# Copy the rest of the application code
COPY . .

# Expose port 80
EXPOSE 80

# Define the command to run the application
CMD ["python", "GenAI.py"]
