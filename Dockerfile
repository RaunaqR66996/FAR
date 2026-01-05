FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
# Ensure src is in pythonpath
ENV PYTHONPATH=/app/src

# Default command (can be overridden in compose)
CMD ["uvicorn", "far.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
