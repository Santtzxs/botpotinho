FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    gcc \
    libssl-dev \
    python3-dev \
    build-essential \
    ffmpeg \              
    libopus0 \            
    libsodium-dev \      
    libffi-dev \          
    && rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho
WORKDIR /app

# Copia dependências Python e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código
COPY . .

# Comando para rodar o bot
CMD ["python", "bot.py"]
