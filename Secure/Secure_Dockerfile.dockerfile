
FROM ubuntu:22.04
# Install system packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    libsqlcipher-dev \
    sqlite3 \
    curl \
    sudo \
    make \
    gcc \
    g++ \
    pkg-config \
    wget \
    gnupg

# Install Python libraries
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy your application files
COPY app.py .
COPY fithealth.db .
COPY cert.pem .
COPY key.pem .

# Expose Flask port
EXPOSE 5000

# Start your server
CMD ["python3", "app.py"]
#CMD ["gunicorn", "-b", "0.0.0.0:5000", "--certfile=cert.pem", "--keyfile=key.pem", "app:app"]