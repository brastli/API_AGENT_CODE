from fastapi import FastAPI

app = FastAPI(title="Hello World API")

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/version")
def version():
    return {"version": "b0f5b64-2026-01-09-05:12"}
