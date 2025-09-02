FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .

ENV DJANGO_SETTINGS_MODULE=trade_india.settings

RUN python manage.py collectstatic --noinput || true

CMD ["gunicorn", "trade_india.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]