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

## Setup and Installation

### Steps to Run the Project

**Clone the repository**:
   ```sh
   git clone https://github.com/ghazaale-r/amazon_product_api.git
   cd amazon_product_api
   ```
**Copy the example environment variables file and customize it**:
    **Using Command Prompt**

    ```sh
        copy .env.example .env
    ```
    
    **Using PowerShell**

    ```sh
        cp .env.example .env
    ```

**Build and start the Docker containers**:

    ```sh
    docker-compose up --build
    ```

**Run the database migrations**:

    For the first time, you need to run these commands manually. After that, migrate and runserver are included in the Dockerfile and will run automatically. 

    ```sh
    docker-compose exec web python manage.py migrate
    docker-compose exec web python manage.py craetesuperuser
    ```

**Access the application**:
    http://localhost:8000
