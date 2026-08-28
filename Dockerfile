FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TRAMITIA_PORT=5050 \
    TRAMITIA_HOST=0.0.0.0 \
    TRAMITIA_DATABASE=/data/tramitia.sqlite3 \
    TRAMITIA_AUDITORIA=/data/tramitia-auditoria.jsonl

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY tramitia/ ./tramitia/
COPY tests/ ./tests/
COPY run.py ./

RUN useradd --create-home --uid 10001 tramitia \
    && mkdir -p /data \
    && chown -R tramitia:tramitia /app /data
USER tramitia

VOLUME ["/data"]
EXPOSE 5050

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5050/health').read()"

CMD ["python", "run.py"]
