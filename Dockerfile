FROM python:3.13-alpine3.21

# Create a user to run the app securely
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends curl openssl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy package and dependencies
COPY requirements.txt .
COPY app/* ./

# Install app dependencies as the apiuser
RUN pip install --no-cache-dir .

# Use non-root user
USER apiuser

# Expose the FastAPI port
EXPOSE 8000

# Add healthcheck for the container
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8000/ || exit 1

CMD ["python3", "main.py"]
