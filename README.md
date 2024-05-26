# Amazon Product API

## Project Overview
This is a Django-based project that allows users to fetch product details from Amazon using web scraping.
The project is Dockerized for easy setup and deployment, and it uses PostgreSQL as the database and Redis for caching.


## Features

- Fetch product details from Amazon by product ID.
- Cache product details in Redis for faster subsequent access.
- Store product details in PostgreSQL.
- Dockerized for easy setup and deployment.


## Technologies and Packages Used

- **Python 3.10**
- **Django**
- **Django Rest Framework (DRF)**
- **PostgreSQL**
- **Redis**
- **Docker**
- **Docker Compose**
- **BeautifulSoup** (for web scraping)
- **Selenium** (for web scraping)
- **django-environ** (for environment variable management (.env file in config root))
- **pytest** (for testing)