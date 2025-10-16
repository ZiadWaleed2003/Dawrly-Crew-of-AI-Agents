FROM python:3.11.13-slim AS base

# Prevents Python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# Ensures logs are flushed directly
ENV PYTHONUNBUFFERED=1

WORKDIR /backend

# Install dependencies first (cached layer)
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy the rest of the source code
COPY . .


ENV PYTHONPATH=/backend


EXPOSE 8000

CMD ["uvicorn", "main:app", "--host=0.0.0.0",  "--port=8000"]

