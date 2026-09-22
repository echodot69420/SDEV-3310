# Assignment 1 API Tests

This repository contains an HTTP test runner for the Assignment 1 Library Management System API. The application itself is not stored here; start the API from its own project before running these tests.

## Setup

Create and activate a virtual environment, then install the test dependency:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

The test runner expects the API at `http://127.0.0.1:8000`. Start the API before running the tests:

```powershell
python tests\assignment-1\test_api.py
```

The runner checks the health endpoint, all member and book endpoints, relationship behavior, duplicate records, missing resources, and representative validation errors. It creates temporary records and deletes them during the run.

## Results

Each run writes a human-readable report to:

```text
tests/assignment-1/results.md
```

The report includes every request, expected and actual status codes, response details, and the overall pass/fail count.

## Project Structure

```text
tests/
└── assignment-1/
    └── test_api.py
requirements.txt
README.md
```
