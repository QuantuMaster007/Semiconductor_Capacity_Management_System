FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data/raw data/processed reports

EXPOSE 8050

ENV PYTHONUNBUFFERED=1
ENV PORT=8050

# Generate data first, then launch with gunicorn (production WSGI server)
CMD python main.py --generate && \
    gunicorn --chdir dashboards \
             --bind 0.0.0.0:${PORT} \
             --workers 1 \
             --timeout 300 \
             --preload \
             "interactive_dashboard:server"
