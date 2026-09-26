# Faratabesh — E-Commerce REST API

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/Django%20REST%20Framework-3.16-A30000?logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-broker-DC382D?logo=redis&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-async%20tasks-37814A?logo=celery&logoColor=white)
![JWT](https://img.shields.io/badge/Auth-JWT-black?logo=jsonwebtokens&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-dev%20%26%20prod-2496ED?logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-reverse%20proxy-009639?logo=nginx&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

A full-featured e-commerce backend built with **Django REST Framework**, powering the storefront for **Faratabesh**. The backend was built to match a custom UI/UX design created specifically for this store — not as a generic, template-based e-commerce API.

This was my first real-world project, built to apply everything from API design and JWT authentication to background task processing and payment gateway integration in a production-oriented setup.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Docker & Infrastructure](#docker--infrastructure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Notes on Production Deployment](#notes-on-production-deployment)
- [License](#license)
- [Author](#author)

## Overview

Faratabesh is a backend-only REST API for an online store, built to serve a custom-designed frontend rather than acting as a generic, reusable e-commerce template. It covers the full commerce flow — from browsing categorized products to checkout, payment, and order tracking — along with SMS-based verification and background job processing.

## Key Features

- 🔐 **JWT Authentication** — token-based auth via `djangorestframework-simplejwt` and `dj-rest-auth`
- 📱 **SMS Verification** — phone number verification / OTP flow powered by **sms.ir**
- 🗂️ **Two-level Category Hierarchy** — parent categories → child categories, with products belonging to child categories
- 🛒 **Shopping Cart** — full cart management (add, update, remove items)
- 📦 **Order System** — order creation, tracking, and status management
- 💳 **Payment Gateway Integration** — **ZarinPal**, via `az-iranian-bank-gateways` (which supports easily adding more Iranian gateways later)
- 🌐 **Multi-language Content Support** — model-level translations via `django-parler` / `django-parler-rest`
- 📝 **Rich Text Content** — product descriptions and content editing via `django-ckeditor-5`
- ⚙️ **Background Task Processing** — async jobs (e.g. notifications) handled by **Celery**, with **Redis** as the broker
- 📖 **Auto-generated API Docs** — OpenAPI schema and interactive docs via `drf-spectacular` (Swagger UI & Redoc)
- 🛠️ **Admin Panel** — Django's built-in admin, extended with `django-colorfield` for visual attributes (e.g. color variants)
- 📰 **Blog** — content pages and posts, separate from the product catalog
- 🎟️ **Promotions** — discounts, coupons, and promotional campaigns
- 🆘 **Helpdesk** — customer support ticketing built into the storefront

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 5.2, Django REST Framework |
| Authentication | JWT (`simplejwt`, `dj-rest-auth`) |
| Database | PostgreSQL |
| Broker / Cache | Redis |
| Async Tasks | Celery |
| Payment | ZarinPal (`az-iranian-bank-gateways`) |
| SMS | sms.ir |
| i18n | django-parler / django-parler-rest |
| Rich Text | django-ckeditor-5 |
| API Docs | drf-spectacular |
| Static Files (prod) | whitenoise |
| App Server (prod) | Gunicorn |
| Containerization | Docker, Docker Compose (separate dev & prod configs) |

## API Documentation

Interactive, auto-generated API documentation is available via `drf-spectacular`:

- **Swagger UI:** `/swagger/`
- **Redoc:** `/redoc/`
- **Raw OpenAPI schema:** `/schema/`

> Paths are relative to your project's root URL configuration (e.g. `http://localhost:8000/swagger/`).

## Project Structure

```
blog/           Blog posts and content pages
product/        Product catalog, two-level category hierarchy, rich-text descriptions, translations
user/           Custom user model, JWT auth, phone verification (SMS OTP)
order/          Cart, order creation, status, and history
helpdesk/       Customer support tickets
payments/       ZarinPal payment gateway integration
promotions/     Discounts, coupons, and promotional campaigns
shop/           Core storefront logic tying the above apps together
```

## Docker & Infrastructure

The project uses **separate Docker Compose files for development and production**.

### Development — `docker-compose.dev.yml`

Only the dependent services (**PostgreSQL** and **Redis**) run in Docker; Django and Celery run directly on the host via `runserver` and `celery worker` for faster iteration.

```bash
docker compose -f docker-compose.dev.yml up -d
```

### Production — `docker-compose.prod.yml`

Fully containerized: **Django** (via Gunicorn), **Celery worker**, **PostgreSQL**, and **Redis** all run as separate services.

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Production images are based on `python:3.12-slim`, and the app is served with **Gunicorn** behind the container's exposed port.

## Getting Started

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- PostgreSQL 15 (via Docker in dev)
- Redis (via Docker in dev)

### Development Setup

```bash
# 1. Clone the repository
git clone <repository-url>
cd faratabesh

# 2. Start dependent services (PostgreSQL, Redis)
docker compose -f docker-compose.dev.yml up -d

# 3. Create a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 4. Install development dependencies
pip install -r requirements/development.txt

# 5. Copy .env.example to .env and fill in your values (see Environment Variables below)
cp .env.example .env

# 6. Run migrations
python manage.py migrate

# 7. Create an admin account
python manage.py createsuperuser

# 8. Run the development server
python manage.py runserver

# 9. In a separate terminal, run the Celery worker
celery -A config worker --loglevel=info
```

## Environment Variables

Copy `.env.example` to `.env` and fill in your own values:

```env
SECRET_KEY=change-me

# Database
POSTGRES_USER=postgres
POSTGRES_DB=commerce
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Django
DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1
DJANGO_SECURE_COOKIES=False

# Payment (ZarinPal)
ZARINPAL_MERCHANT_CODE=length-36

# SMS (sms.ir)
SMS_API_KEY=your_api_key
SMS_USERNAME=your_username
SMS_LINE=your_line_number
```

> Set `DEBUG=True` and `DJANGO_SECURE_COOKIES=False` for local development; flip both for production, and make sure `POSTGRES_HOST` matches your setup (`db` for Docker, `localhost` if running Postgres outside Docker).
>
> `docker-compose.dev.yml` reads its Postgres credentials from `.env.development` — copy the same `POSTGRES_*` values there as well (or symlink it to `.env`).

## Notes on Production Deployment

- `DEBUG=False` and a properly configured `ALLOWED_HOSTS` are required before going live
- Static files are served via **whitenoise** in production
- The production Dockerfile installs only `requirements/production.txt` — development-only tools (like linters or debug packages) are excluded from the production image
- The Celery worker runs as its own container in production (`docker-compose.prod.yml`), separate from the Django web process

## License

This project is licensed under the MIT License. *(Update this if you'd prefer a different license or want the code kept proprietary.)*
