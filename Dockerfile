FROM python:3.11-slim-bookworm

RUN apt-get update && apt-get install -y \
    gcc \
    git \
    libssl-dev \
    python3-dev \
    build-essential \
    ffmpeg \
    libopus-dev \
    libsodium-dev \
    libffi-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-u", "bot.py"]
