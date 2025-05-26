FROM python:3.12.10-alpine3.21

# Create a user to run the app securely
WORKDIR /app

# Copy package and dependencies
COPY pyproject.toml ./
COPY app/* ./

# Install app dependencies as the apiuser
RUN pip install --no-cache-dir .

# Use non-root user
USER apiuser

EXPOSE 8000

CMD ["python3", "main.py"]
