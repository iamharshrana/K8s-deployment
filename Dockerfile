# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Copy the environment variables file
COPY .env /app/.env

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000 to the outside world
EXPOSE 5000

# Set environment variables to be used by Flask
ENV FLASK_APP=app.py

# Run the application when the container launches
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
