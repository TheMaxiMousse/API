# ChocoMax API

API service for the **ChocoMax** shop site, delivering essential business logic and data through a modern, FastAPI-powered interface.

This repository serves as the core **API application** for ChocoMax. It handles product listings, orders, user preferences, and more — enabling both the website and any future clients (like mobile apps) to interact with the system.

---

## 🧾 About ChocoMax API

**ChocoMax** is a growing project focused on bringing chocolate lovers a modern, efficient way to shop online.

This API repository powers:

- 📦 Product and order management
- 🔐 Authentication and user preferences
- 🌍 Multi-language support
- ⚙️ Internal and public API endpoints

🗓️ **Started:** 2025
🚀 **Status:** In active development

## 📦 What’s in this Repository?

- FastAPI-based API
- RESTful endpoints with API versioning
- Docker and DevContainer support
- Packageable as a Python module

> [!NOTE]
> This repository contains only the API logic. It does not include front-end assets, user interfaces, or any kind of data storage.

## 🧭 Project Resources

- 🧪 [ChocoMax API Tests](./tests) — Unit and integration test cases
- 🐳 [.devcontainer/](.devcontainer/) — Containerized development setup
- 📄 [`Dockerfile`](./Dockerfile) — Production-ready Docker image
- ⚙️ [`setup.py`](./setup.py) — Python packaging configuration

## 🛠️ Tech Stack

- [FastAPI](https://fastapi.tiangolo.com) — Web framework
- [Docker](https://www.docker.com) — Containerized builds and deployments
- [Dev Containers](https://containers.dev) — Reproducible development environments
- [VS Code Tasks](https://code.visualstudio.com/docs/editor/tasks) — Custom automation

## ⚙️ Devcontainer

A ready-to-use **development container** is defined in `.devcontainer/`. Features:

- 🐧 Alpine-based image with FastAPI.
- 🚀 Launches a fully functional API and DB environment with one command
- 📎 Includes VS Code extensions and automation tasks (build, test)

### ▶️ Getting Started (DevContainer)

1. Open the repository in **Visual Studio Code**
2. Select **“Reopen in Container”**
3. Run the `Start FastAPI server` task (or use `uvicorn` manually)

## 📦 Building the Project

### 🔧 As a Docker Image

```bash
docker build -t chocomax-fastapi-image .
docker run -d -p 8000:8000 --name chocomax-api-container chocomax-fastapi-image
```

Then visit: [http://localhost:8000](http://localhost:8000)

### 📦 As a Python Package

Generate the package (without installing it locally):

```bash
# Clean previous build artifacts and generate a fresh Python package
python setup.py clean --all sdist bdist_wheel
```

> This will create a `dist/` directory containing your `.whl` and `.tar.gz` packages.

## 🤝 Contributing

If you’d like to help improve the API or suggest new features:

1. Fork this repository
2. Create a feature branch
3. Submit a pull request with clear description and rationale

We welcome ideas around security, performance, and developer experience.

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

Thanks for using **ChocoMax API**!
For more details about the ChocoMax platform, stay tuned for upcoming documentation and repositories.
