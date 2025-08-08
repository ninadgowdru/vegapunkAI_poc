import os
import requests
from dotenv import load_dotenv
import json
import re

# Load .env
load_dotenv()

# Provider keys from .env
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Base URLs
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

def generate_poc_prompt(vuln_description, target, language="python"):
    return f"""
You are an expert penetration tester and exploit developer.
Given the following vulnerability description, produce a clear, minimal, and safe Proof-of-Concept (PoC) code snippet 
and also a short explanation and remediation steps.
Return a JSON object with keys: 'poc_code', 'explanation', 'remediation'.

Vulnerability description:
{vuln_description}

Target:
{target}

Language: {language}

Constraints:
- The PoC should demonstrate the concept but avoid causing harm or data destruction.
- Provide one or two short example payloads if applicable.
- Keep the PoC under 100 lines when possible.
"""

def call_openrouter(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistralai/mixtral-8x7b-instruct",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 800
    }
    response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
    return response.json()

def call_groq(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 800
    }
    response = requests.post(GROQ_URL, headers=headers, json=payload)
    return response.json()

def call_gemini(prompt):
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(GEMINI_URL, headers=headers, params=params, json=payload)
    return response.json()

def extract_response(content):
    match = re.search(r"\{.*\}", content, re.S)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return {"poc_code": content, "explanation": "", "remediation": ""}
    return {"poc_code": content, "explanation": "", "remediation": ""}

def generate_poc(vuln_description, target, language="python"):
    prompt = generate_poc_prompt(vuln_description, target, language)

    # Provider failover order: OpenRouter → Groq → Gemini
    providers = [
        ("OpenRouter", OPENROUTER_API_KEY, call_openrouter, lambda r: r["choices"][0]["message"]["content"]),
        ("Groq", GROQ_API_KEY, call_groq, lambda r: r["choices"][0]["message"]["content"]),
        ("Gemini", GEMINI_API_KEY, call_gemini, lambda r: r["candidates"][0]["content"]["parts"][0]["text"])
    ]

    for name, key, func, extract_func in providers:
        if not key:
            print(f"⚠️ Skipping {name} — no API key in .env")
            continue
        try:
            print(f"🔄 Trying {name}...")
            data = func(prompt)
            if "error" in data:
                print(f"❌ {name} error: {data['error']}")
                continue
            content = extract_func(data)
            return extract_response(content)
        except Exception as e:
            print(f"❌ {name} failed: {e}")
            continue

    return {"error": "All providers failed", "poc_code": "", "explanation": "", "remediation": ""}

