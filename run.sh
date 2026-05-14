#!/bin/bash
# AiYou FastAPI Services - Run Script

echo "Starting AiYou FastAPI Services - Cor.57 Unified Sky-Ground GPU Mesh"
echo "=================================================================="
echo ""
echo "API will be available at:"
echo "  - Swagger UI: http://localhost:8000/docs"
echo "  - ReDoc: http://localhost:8000/redoc"
echo "  - Health Check: http://localhost:8000/health"
echo ""

# Run the application
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
