# Minimal Dockerfile for whispered desire bot
FROM python:3.11-slim

WORKDIR /app

# install build deps if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Use environment variable for token at runtime
ENV DB_PATH=/data/whispers.db
VOLUME ["/data"]

CMD ["python", "bot.py"]