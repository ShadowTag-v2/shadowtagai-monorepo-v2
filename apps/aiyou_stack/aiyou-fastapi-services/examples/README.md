# Examples

This directory contains example scripts demonstrating how to use the Analytics Engineer API.

## Prerequisites

Make sure the API is running:

```bash
# Using Docker
docker-compose up -d

# Or locally
uvicorn src.main:app --reload
```

Install the httpx library for running examples:

```bash
pip install httpx
```

## Examples

### Basic Usage

`basic_usage.py` - Demonstrates core functionality:

- Tracking events
- Getting event statistics
- Creating conversion funnels
- Analyzing funnels
- Creating dashboards
- Analyzing user behavior
- Generating insights

Run it:

```bash
python examples/basic_usage.py
```

## More Examples

You can create additional examples for:

- Advanced funnel analysis
- Custom dashboard creation
- Time series queries
- User segmentation
- Batch event processing
- Real-time analytics

## API Documentation

For complete API documentation, visit:

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>
