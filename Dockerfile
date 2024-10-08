# Use official Python image as a base
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY . .

# Environment-specific variables will be injected at runtime
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
