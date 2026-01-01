# Fratabesh

Fratabesh is an online store for bags built with Django.

## Project Structure

- **Dockerized setup** for both development and production
  - `docker-compose.dev.yml` for development
  - `docker-compose.prod.yml` for production
  - `Dockerfile` for building the Django container
- **Requirements**
  - `requirements/development.txt` for development dependencies
  - `requirements/production.txt` for production dependencies

## Environment

- Development uses `.env.development`
- Production uses `.env`
- `.env.example` contains all required environment variables
