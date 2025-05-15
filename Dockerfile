FROM python:3.12.3-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_BROWSERS_PATH=/playwright-browsers

WORKDIR /app

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends git libnss3-tools xvfb x11-utils xauth && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install -r requirements.txt

COPY . .

RUN git clone --recurse-submodules https://github.com/Sana451/scraping_tools.git /app/scraping_tools

COPY scrapoxy-ca.crt /tmp/scrapoxy-ca.crt
COPY scrapoxy-ca-linux-server.crt /tmp/scrapoxy-ca-linux-server.crt

RUN mkdir -p /root/.pki/nssdb && \
    certutil -N -d sql:/root/.pki/nssdb --empty-password && \
    certutil -A -d sql:/root/.pki/nssdb -t "C,," -n scrapoxy -i /tmp/scrapoxy-ca.crt && \
    certutil -A -d sql:/root/.pki/nssdb -t "C,," -n scrapoxy-prod -i /tmp/scrapoxy-ca-linux-server.crt && \
    cp /tmp/scrapoxy-ca.crt /usr/local/share/ca-certificates/scrapoxy.crt && \
    cp /tmp/scrapoxy-ca-linux-server.crt /usr/local/share/ca-certificates/scrapoxy-prod.crt && \
    update-ca-certificates && \
    rm /tmp/scrapoxy-ca.crt /tmp/scrapoxy-ca-linux-server.crt

RUN playwright install --with-deps chromium && \
    mkdir -p $PLAYWRIGHT_BROWSERS_PATH && \
    chmod -Rf 777 $PLAYWRIGHT_BROWSERS_PATH

RUN mkdir -p /app/alkoteka_com/results && chmod -R 777 /app/alkoteka_com/results


CMD ["sh", "-c", "xvfb-run --auto-servernum scrapy crawl $SPIDER_NAME -O $RESULTS_FILE_PATH"]
