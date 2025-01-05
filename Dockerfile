# base image
FROM python:3.12-slim-bullseye

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY src src
COPY .env .

WORKDIR /app/src

# Expose the port the app runs on
EXPOSE 8000

# Command to run the FastAPI app
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]