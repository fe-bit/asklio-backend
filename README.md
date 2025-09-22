# Procurement Request Backend (FastAPI)

This project is a backend REST API for managing procurement requests, designed for easy integration with a web-based frontend. It supports request creation, automatic commodity group assignment using AI, PDF extraction, CRUD operations, and status tracking.

## Features

- **Create, Read, Update, Delete Procurement Requests**
- **Automatic Commodity Group Assignment** using AI (OpenAI or Gemini)
- **PDF Extraction Endpoint**: Auto-fill procurement requests from PDF offers
- **Status Tracking**: Open, In Progress, Closed
- **Commodity Group Management**: All groups stored in the database
- **Mock Data**: Easily populate with sample requests for testing
- **Async Endpoints**: Fast and scalable
- **CORS Enabled**: Ready for frontend integration

## Tech Stack

- **FastAPI** (Python)
- **SQLite** (default, easy to swap for other DBs)
- **LangChain** (for AI-powered extraction and classification)
- **Docker** & **Docker Compose** (for deployment)
- **Pydantic** (for validation and DTOs)

## Setup

### 1. Clone the Repository

```sh
git clone asklio-backend
cd asklio-backend
```

### 2. Install Dependencies

```sh
pip install poetry
poetry install --no-root
```

### 3. Environment Variables

Create a `.env` file with your API keys:

```
OPENAI_API_KEY=your-openai-key
GOOGLE_API_KEY=your-google-api-key
```

### 4. Run the App

```sh
uvicorn src.main:app --reload
```

and for production:

```sh
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```
### 5. API Docs

Visit [http://localhost:8000/docs](http://localhost:8000/docs) for interactive Swagger documentation.

## Endpoints

- `POST /requests` — Create a new procurement request (commodity group auto-assigned)
- `GET /requests` — List all requests
- `GET /requests/{id}` — Get a request by ID
- `PUT /requests/{id}` — Update a request
- `DELETE /requests/{id}` — Delete a request
- `POST /extract-pdf` — Upload a PDF offer and auto-fill request fields
- `GET /commodity-groups` — List all commodity groups

## Mock Data

On startup, the app automatically inserts sample procurement requests and all commodity groups into the database if not present.

## Contributing

Pull requests and issues are welcome! Please follow standard Python and FastAPI best practices.

## License

MIT License
