from fastapi import FastAPI
from app.api.v1.endpoints.routes import router as v1_router
from app.api.v1.endpoints.candidates import router as candidates_router

app = FastAPI(title="AI Resume Screening API")

app.include_router(v1_router, prefix="/api/v1", tags=["Health"])
app.include_router(candidates_router, prefix="/api/v1", tags=["Candidates"])