from fastapi import FastAPI

app = FastAPI(
    title="AEGIS AI API",
    description="Network Traffic Intelligence Platform",
    version="0.5.0"
)


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": "AEGIS AI API"
    }