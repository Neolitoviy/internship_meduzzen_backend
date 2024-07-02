
# FastAPI Project

## Dependencies

- Python 3.10

## Installation

### 1. Clone the Repository

Clone the repository to your local machine:

```bash
git clone https://github.com/Neolitoviy/internship_meduzzen_backend.git
cd internship_meduzzen_backend
```

### 2. Create a Virtual Environment

Create and activate a virtual environment:

#### For Windows:
```bash
python -m venv venv
venv\Scripts\activate.bat
```

#### For MacOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

Install the required packages using `pip`:

```bash
pip install -r requirements.txt
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