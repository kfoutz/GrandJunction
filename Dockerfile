FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app

# create non-root user
RUN useradd -m appuser || true
RUN chown -R appuser:appuser /app
USER appuser

CMD ["gunicorn", "manage:app", "-c", "gunicorn.conf.py"]

  
