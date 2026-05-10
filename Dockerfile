FROM docker.arvancloud.ir/python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements/production.txt /app/requirements/production.txt
RUN pip install --no-cache-dir -r /app/requirements/production.txt --root-user-action=ignore

COPY . /app

EXPOSE 8000

CMD ["gunicorn", "commerce_back.wsgi:application", "--bind", "0.0.0.0:8000"]
