FROM python:3.11-slim


WORKDIR /app

#Instalar dependências do sistema e o Google Chrome

RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    wget \
    unzip \
    --no-install-recommends && \
    curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/keyrings/google-chrome.gpg && \
    sh -c 'echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list' && \
    apt-get update && apt-get install -y \
    google-chrome-stable \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

#Instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY ./app /app/app



EXPOSE 8521
# O caminho da aplicação
CMD ["gunicorn", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8521", "app.main:app"]