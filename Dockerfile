# Use lightweight Python base image
FROM python:3.11-slim

# Set environment variables to optimize Python runtime in container
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory to /app
WORKDIR /app

# Copy dependency requirements first for Docker layer caching optimization
COPY requirements.txt .

# Install dependencies without using pip cache
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 8000
EXPOSE 8000

# Run the FastAPI app using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
