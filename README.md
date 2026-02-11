# VP Core

Core utilities and helpers for VP projects.

## Features

- **Structured Logging**: JSON-formatted logging with support for Pydantic models and context tracking.
- **FastAPI Middleware**: Out-of-the-box middleware for request/response logging, request ID generation, and performance tracking.
- **Helpers**: Common utility functions for case conversion, JSON parsing, and more.

## Installation

You can install this package directly from GitHub:

```bash
pip install git+https://github.com/Volopay/vp-python-core.git
```

Or add it to your `pyproject.toml`:

```toml
dependencies = [
    "vp-core @ git+https://github.com/Volopay/vp-python-core.git"
]
```

## Usage

### Logging

```python
from vp_core import setup_logging, get_logger

# Initialize logging at the start of your application
setup_logging()

logger = get_logger(__name__)
logger.info("Application started", extra={"version": "1.0.0"})
```

### Helpers

```python
from vp_core.helpers.case_converter import to_camel

camel_case = to_camel("snake_case_string")
# Output: "snakeCaseString"
```

### FastAPI Middleware

To use the logging middleware in a FastAPI application:

```python
from fastapi import FastAPI
from vp_core.logging.middleware import logging_middleware

app = FastAPI()
app.middleware("http")(logging_middleware)
```

Note: Requires `fastapi` to be installed. You can install it with the package using:
```bash
pip install "vp-core[fastapi] @ git+https://github.com/YOUR_USERNAME/vp-core.git"
```

## Development

### Running Tests and Benchmarks

This package uses `pytest` for testing, `pytest-cov` for coverage, and `pytest-benchmark` for benchmarking.

First, install the test dependencies:
```bash
pip install -e ".[test]"
```

To run tests:
```bash
pytest
```

To run benchmarks:
```bash
pytest --benchmark-only
```

### Running Checks
