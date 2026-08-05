import httpx

r = httpx.post("http://localhost:11434/api/generate",
    json={"model": "llama3.2:3b", "prompt": "Hola", "stream": False},
    timeout=60)

print(r.json()["response"])
