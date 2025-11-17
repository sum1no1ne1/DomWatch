FROM python:3.9-slim

# Install Chromium and other dependencies
RUN apt-get update && \
    apt-get install -y wget gnupg && \
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Install chromedriver
RUN CHROMEDRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
    wget -N http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip -P ~/ && \
    unzip ~/chromedriver_linux64.zip -d ~/ && \
    rm ~/chromedriver_linux64.zip && \
    mv ~/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE $PORT

# Start command
CMD gunicorn app:app