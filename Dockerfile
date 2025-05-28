FROM python:3.13-alpine3.21

# Create a non-root user
RUN adduser --disabled-password --gecos "" apiuser
WORKDIR /chocomax

# Install runtime dependencies
RUN apk add --no-cache curl openssl

# Copy requirements and all source files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir .

# Use non-root user after installation
USER apiuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8000/ || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
