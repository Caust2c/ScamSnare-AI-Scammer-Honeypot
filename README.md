# Project Setup and Run Guide

## Prerequisites

- Python 3.10+
- Ollama installed and available in PATH
- Virtual environment (`venv`) created in the project root

---

## Start Ollama

Before starting the backend server, ensure Ollama is running:

```bash
ollama serve
```

Pull the required model:

```bash
ollama pull llama3.2:3b
```
You can use any other model as well
Make sure Ollama is running before starting the backend server.

---

## Backend Setup

### 1. Create Virtual Environment (if not already created)

```bash
python -m venv venv
```

### 2. Configure API Key

Set your API key inside `config.py`. Also update the API key in the frontend script.js file(marked in comments).

### 3. Run the Server

Start the backend using the provided shell script:

```bash
bash shell.sh
```

#### What `shell.sh` Does

The shell script performs the following operations:

## Server URL

Once started, the server runs at:

```
http://localhost:8000
```

If running on a remote machine:

```
http://<your-server-ip>:8000
```

---

## API Documentation

FastAPI automatically provides interactive API documentation at:

```
http://localhost:8000/docs
```

Visit this URL in your browser to explore and test all available API endpoints.