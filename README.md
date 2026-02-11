# ScamSnare - An AI-Powered Adaptive Scam Honeypot

## More about the project
ScamSnare is a basic AI-powered honeypot built to interact with scam messages in a safe, controlled environment. It simulates a realistic victim persona using a locally hosted language model, allowing the system to study how scammers operate without putting real users at risk.

The goal of the project is to analyze scam patterns, extract useful threat intelligence, and improve automated scam detection. It runs on a FastAPI backend that connects the AI agent, detection logic, and intelligence extraction pipeline into one system.

ScamSnare is designed for cybersecurity research and defensive AI experimentation, providing a practical way to observe and understand modern social engineering tactics.
![demo](image.png)

---

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
You can use any other model as well but do change it in agent_engine.py
Make sure Ollama is running before starting the backend server.

---

## Prompt modification

You can modify the prompt in agent_engine.py. By default its set to have a believable persona, you can modify it entirely or just give a light personality change.

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