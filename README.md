# IS601 - Module 11: Secure FastAPI Application

This project is a FastAPI application that provides a simple calculator API and a complete, secure user authentication system.The application uses SQLAlchemy with a Postgres database, Pydantic for all schema validation, and passlib for secure password hashing. The entire project is containerized with Docker and includes a full CI/CD pipeline for automated testing, security scanning, and deployment.

## Prerequisites
- Python 3.10+
- Docker & Docker Compose

## Running the Application (Local Development)

This project is designed to run with Docker Compose, which manages the FastAPI web service, the Postgres database, and a pgAdmin instance

Clone the repository:
git clone [https://github.com/MohammedSaim-Quadri/assignment10_is601](https://github.com/MohammedSaim-Quadri/assignment10_is601)

cd assignment10_is601

## Set up a local virtual environment (for IDEs and testing):
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Build and run the containers:
```bash
docker compose up --build
```

The application will start with hot-reloading.
- API: http://localhost:8000API
- Docs (Swagger): http://localhost:8000/docs
- pgAdmin: http://localhost:5050

login and pwd details in docker compose

## How to Run Tests Locally

The test suite includes unit, integration, and E2E tests. The integration tests are configured to run against the live, containerized test database.

1. Ensure the containers are running:
You must have the Docker services running first, as the integration tests require a live database connection.```bash
docker compose up
```

2. Run the tests:
In a new terminal window, activate your local virtual environment and run pytest.# Activate your local environment
```bash
source venv/bin/activate
```

## Run all tests (User tests + Calculation tests)
pytest

## --- Run only the new Module 11 tests ---
pytest tests/integration/test_calculation.py -v
pytest tests/integration/test_calculation_schema.py -v

## Run Tests with Coverage Report:
To generate a coverage report for the app/ directory, use:
```bash
pytest --cov=app
```

## CI/CD Pipeline & Docker Hub:
This repository is configured with a full CI/CD pipeline using GitHub Actions. On every push to main, the following jobs are executed:
- Test: Spins up a Postgres service, installs dependencies, and runs the entire pytest suite.
- Security: Builds the Docker image and scans it for CRITICAL or HIGH vulnerabilities using Trivy.
- Deploy: If the tests and scan pass, the pipeline pushes the validated image to Docker Hub.
Docker Hub Repository Link:https://hub.docker.com/r/saimquadri/601_module11