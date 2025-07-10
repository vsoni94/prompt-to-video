FROM python:3.10-slim

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    ffmpeg \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements and install packages
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copy source code
# Copy only the app folder contents into /app
COPY app/ ./app/

# Copy celery_worker.sh to /app (or / depending on your preference)
COPY celery_worker.sh /app/

# Make sure the script is executable
RUN chmod +x /app/celery_worker.sh

# Expose FastAPI default port
EXPOSE 8000

# Start FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


# docker build -t varunsoni94/text2video-api .
# docker push varunsoni94/text2video-api
