
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

Otherwise it should return an error message.