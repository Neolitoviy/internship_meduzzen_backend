
# FastAPI Project

## Dependencies

- Python ^3.10
- Docker
- Docker Compose

## Installation

### 1. Clone the Repository

Clone the repository to your local machine:

```bash
git clone https://github.com/Neolitoviy/internship_meduzzen_backend.git
cd internship_meduzzen_backend
```

### 2. Install Poetry

Create and activate a virtual environment:

Follow the instructions on [Poetry's official website to install Poetry](https://python-poetry.org/docs/#installing-with-the-official-installer).

### 3. Install Dependencies

Install the required packages using poetry:

```bash
poetry install
```

## Running the Application

To start the FastAPI application with Uvicorn, use the following command:

```bash
uvicorn app.main:app --reload
```

This will start the application, and it will be accessible at `http://127.0.0.1:8000/`.

## Health Check Endpoint

You can check if the application is running by accessing the health check endpoint:

### Via Browser:

Navigate to the following URL in your browser:

```http
http://127.0.0.1:8000/
```

It should return a JSON response:

```json
{
    "status_code": 200,
    "detail": "ok",
    "result": "working"
}
```

### Via Swagger UI:

Open the Swagger UI documentation at:

```http
http://127.0.0.1:8000/docs
```

Here you can see the available endpoint and test the GET / endpoint directly from the browser.

## Running Tests

### 1. Run Tests

My Coverage html report:

![image](https://github.com/user-attachments/assets/c14c1b14-1386-496c-b071-71ecf4fbe6b7)
![image](https://github.com/user-attachments/assets/86c46076-769c-4fc0-8b5b-9f7a6d68370e)
![image](https://github.com/user-attachments/assets/0c19618c-3e07-443d-b30a-edcbc16ee7bd)
![image](https://github.com/user-attachments/assets/e3829866-e931-47c7-a827-30d43b551a35)

Run the tests using the following command:

```bash
pytest
```

This will discover and run all the test files in project.

### 2. Running Tests in Docker

To run tests in the Docker container:

#### List all running containers:

```bash
docker ps
```

This command displays all running containers. Note the ID of your container.

#### Open a terminal in the container:

```bash
docker exec -it [CONTAINER ID] bash
```

Replace `[CONTAINER ID]` with the actual ID of your container.

#### Run tests in the container terminal:

```bash
pytest
```
### 3. Running Tests with coverage report

```bash
pytest --cov=./app --cov-report=xml --cov-report=html
```

### 4. View a report on the command line

```bash
coverage report -m
```

### 5. HTML report generation

```bash
coverage html
```

## Running the Application with Docker

### 1. Build the Docker Image

```bash
docker build -t fastapi-app .
```

### 2. Run the Docker Container

```bash
docker run -d -p 8000:8000 --name fastapi-app-container --env-file .env fastapi-app
```

### 3. Verify the Application

### Via Browser:

Navigate to the following URL in your browser:

```http
http://127.0.0.1:8000/
```

It should return a JSON response:

```json
{
    "status_code": 200,
    "detail": "ok",
    "result": "working"
}
```

### Via Swagger UI:

Open the Swagger UI documentation at:

```http
http://127.0.0.1:8000/docs
```

Here you can see the available endpoint and test the GET / endpoint directly from the browser.

## Running the Application with Docker Compose

### 1. Build and Run

```bash
docker-compose up --build
```

This command will start the PostgreSQL, Redis, and FastAPI services. The FastAPI application will be accessible at http://localhost:8000.

### 2. Stop Services

```bash
docker-compose down
```

### 3. View Logs:

#### To view the logs for a specific service, use:

```bash
docker-compose logs <service_name>
```

### 4. Verify the Application

### base_status Endpoint:

The /base_status endpoint checks the connection status of both PostgreSQL and Redis databases.

```http
http://127.0.0.1:8000/base_status
```

It should return a JSON response:

```json
{
    "postgres_status": "connected",
    "redis_status": "connected"
}
```

Otherwise, it should return an error message.

## Creating and Applying Migrations

### 1. Prerequisites

```bash
poetry install
```

### 2. Initialize Alembic:

```bash
alembic init migrations
```

This command will create a migrations directory with Alembic configuration files.

### 3. Configure .env

### 4. Creating Migrations

#### 1. Generate a new migration:

```bash
alembic revision --autogenerate -m "Initial migration"
```
This command will generate a new migration script inside the migrations/versions directory.

### 5. Applying Migrations

#### 1. Apply the migrations:

```bash
alembic upgrade head
```

This command will apply all pending migrations to your database.

Alternatively, you can specify a particular revision to upgrade to:

```bash
alembic upgrade <revision>
```

Replace <revision> with the desired revision identifier from one of the generated files in migrations/versions.

## Running Migrations in Docker

```bash
docker-compose exec web alembic upgrade head
```

## Linting commands

### 1. Run Black to format code:

```bash
poetry run black .
```

### 2. Run Isort to sort imports:

```bash
poetry run isort .
```

### 3. Run Flake8 to check for style violations:

```bash
poetry run flake8 .
```

## Celery

### 1. Start Redis server.

### 2. Start Celery worker:

```bash
celery -A app.celery:celery worker --loglevel=INFO
```

### 3. Start Celery worker(Windows):

```bash
celery -A app.celery:celery worker --loglevel=INFO --pool=solo
```

### 4. Start Celery beat (scheduler):

```bash
celery -A app.celery:celery beat --loglevel=INFO
```

### 5. Start Flower (Celery monitoring tool):

```bash
poetry run celery -A app.celery:celery flower --port=5555
```
It will be at:

```http
http://127.0.0.1:5555
```
