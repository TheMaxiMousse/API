# ChocoMax API

This is the API for the ChocoMax site, providing essential services and data to support site functionality.

## Getting Started

To run the API locally, you’ll need:

- **Docker** to build and run the application in a container.

### Setup Steps

1. **Build the Docker Image**:
   ```bash
   docker build -t chocomax-fastapi-image .
   ```
2. **Run the Docker Container**:
   ```bash
   docker run -d -p 8000:8000 --name chocomax-api-container chocomax-fastapi-image
   ```
3. **Access the API**:
   Open your browser or API client to `http://localhost:8000`.
