"""
Backend entrypoint. Run karne ke liye (backend/ folder ke andar se):
    uvicorn app.main:app --reload

Docs yaha khulenge: http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import FRONTEND_ORIGINS
from app.routers import search

app = FastAPI(
    title="Bangalore Transit App API",
    description="Feature 1: Map search + nearby-place verification (agentic).",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
