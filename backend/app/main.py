import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from app.api import divinations, interpretations, followup

app = FastAPI(title="六爻解卦平台 API", version="1.0.0")

origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(divinations.router, prefix="/divinations", tags=["divinations"])
app.include_router(interpretations.router, prefix="/divinations", tags=["interpretations"])
app.include_router(followup.router, prefix="/divinations", tags=["followup"])


@app.get("/health")
def health():
    return {"status": "ok"}
