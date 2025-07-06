FROM python:3.9-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    libzmq-dev \
    gnupg-agent \
    && rm -rf /var/lib/apt/lists/*

# Set up the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy the application code
COPY . /app

# Run the application
CMD ["python", "client.py"]

