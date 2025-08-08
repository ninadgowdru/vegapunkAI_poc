# VegapunkAI — PoC Generator (Chat-style UI)

This project provides a Chat-like interface to generate Proof-of-Concept (PoC) snippets for vulnerabilities using OpenAI (GPT-4).

## Quick start (local)

1. Set your OpenAI key:
```bash
export OPENAI_API_KEY="sk-..."
```

2. From project root:
```bash
docker-compose up --build
```

3. Visit: http://localhost:8000/

## File layout
- backend/ - FastAPI backend + ai_poc module
- frontend/ - Static single-page chat-like UI
- Dockerfile, docker-compose.yml

## Safety
This tool generates PoC code for educational/testing in controlled environments only. Do not use on systems without explicit permission.
