FROM docker.arvancloud.ir/python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN CODENAME=$(grep VERSION_CODENAME /etc/os-release | cut -d= -f2) \
 && tee /etc/apt/sources.list <<EOF
deb http://mirror-linux.runflare.com/debian $CODENAME main contrib non-free non-free-firmware
deb http://mirror-linux.runflare.com/debian $CODENAME-updates main contrib non-free non-free-firmware
deb http://mirror-linux.runflare.com/debian-security $CODENAME-security main contrib non-free non-free-firmware
EOF

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/production.txt /app/requirements/production.txt
RUN pip install  --no-cache-dir -r /app/requirements/production.txt --root-user-action=ignore

COPY . /app

EXPOSE 8000
