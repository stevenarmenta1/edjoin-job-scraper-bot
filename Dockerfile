# 1. Use Python environment
FROM python:3.9-slim

# 2. Install dependencies for Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 3. Set working directory
WORKDIR /app

# 4. Copy files
COPY . /app

# 5. Install Python requirements
RUN pip install --no-cache-dir -r requirements.txt

# 6. Run the app using Gunicorn (Production Server)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app", "--timeout", "120"]