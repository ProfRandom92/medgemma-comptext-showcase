"""
FastAPI Backend for MedGemma × CompText Showcase
Integrates the Python compression pipeline with REST API
"""

import sys
import time
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.nurse_agent import NurseAgent
from src.agents.triage_agent import TriageAgent
from src.agents.doctor_agent import DoctorAgent
from src.core.models import PatientState


class ProcessRequest(BaseModel):
    clinical_text: str = Field(..., min_length=10, max_length=5000)


class CompressionResponse(BaseModel):
    original_text: str
    compressed_state: dict
    original_token_count: int
    compressed_token_count: int
    reduction_percentage: float
    compression_time_ms: float


class TriageResponse(BaseModel):
    priority_level: str
    priority_name: str
    reason: str


class DoctorResponse(BaseModel):
    recommendation: str
    processing_time_ms: float


class PipelineResponse(BaseModel):
    compression: CompressionResponse
    triage: TriageResponse
    doctor: DoctorResponse
    total_time_ms: float


# Initialize agents
nurse_agent = NurseAgent()
triage_agent = TriageAgent()
doctor_agent = DoctorAgent()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle"""
    print("🏥 MedGemma × CompText API Starting...")
    print("✓ Nurse Agent initialized")
    print("✓ Triage Agent initialized")
    print("✓ Doctor Agent initialized")
    yield
    print("🛑 API Shutdown")


app = FastAPI(
    title="MedGemma × CompText API",
    description="Privacy-first healthcare AI with 94% token reduction",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration - Production Security
# Only allow specific origins (Vercel + Fly.io)
ALLOWED_ORIGINS = [
    "https://medgemma-comptext-showcase.vercel.app",
    "https://medgemma-api.fly.dev",
    "http://localhost:3000",  # Development only
    "http://localhost:8000",  # Development only
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,  # Security: Set to True only if authentication needed
    allow_methods=["GET", "POST"],  # Explicit methods only
    allow_headers=["Content-Type", "Authorization"],  # Explicit headers only
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "MedGemma × CompText API",
        "version": "1.0.0",
    }


@app.post("/api/process", response_model=PipelineResponse)
async def process_patient_case(request: ProcessRequest):
    """
    Process a clinical case through the full pipeline:
    1. Compression (Nurse Agent)
    2. Triage (Triage Agent)
    3. Clinical Recommendation (Doctor Agent)
    """
    try:
        total_start = time.time()

        # Step 1: Compression (Nurse Agent)
        compression_start = time.time()
        patient_state = nurse_agent.intake(request.clinical_text)
        compression_time = (time.time() - compression_start) * 1000

        # Token counting (simple approximation)
        original_tokens = len(request.clinical_text.split())
        compressed_json = patient_state.to_compressed_json()
        compressed_tokens = len(str(compressed_json).split())
        reduction_percentage = ((original_tokens - compressed_tokens) / original_tokens * 100)

        # Step 2: Triage Assessment
        triage_result = triage_agent.assess(patient_state)

        # Step 3: Doctor Recommendation
        doctor_start = time.time()
        patient_dict = patient_state.model_dump(exclude_none=True)
        doctor_recommendation = doctor_agent.diagnose(patient_dict)
        doctor_time = (time.time() - doctor_start) * 1000

        total_time = (time.time() - total_start) * 1000

        return PipelineResponse(
            compression=CompressionResponse(
                original_text=request.clinical_text,
                compressed_state=compressed_json,
                original_token_count=original_tokens,
                compressed_token_count=compressed_tokens,
                reduction_percentage=max(0, reduction_percentage),
                compression_time_ms=compression_time,
            ),
            triage=TriageResponse(
                priority_level=triage_result["priority_level"],
                priority_name=triage_result["priority_name"],
                reason=triage_result["reason"],
            ),
            doctor=DoctorResponse(
                recommendation=doctor_recommendation,
                processing_time_ms=doctor_time,
            ),
            total_time_ms=total_time,
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/examples")
async def get_example_cases():
    """Get predefined clinical case examples"""
    return {
        "examples": [
            {
                "title": "🫀 Cardiology Case",
                "text": "Chief complaint: chest pain radiating to left arm. HR 110, BP 130/85, Temp 39.2C. Medication: aspirin.",
            },
            {
                "title": "🫁 Respiratory Case",
                "text": "Shortness of breath, wheezing, asthma exacerbation. HR 95, BP 118/76, Temp 38.5C. Triggers: allergens.",
            },
            {
                "title": "🧠 Neurology Case",
                "text": "Slurred speech, left-side weakness, face drooping. Time last known well: 2 hours ago. HR 88, BP 145/92.",
            },
            {
                "title": "🚑 Trauma Case",
                "text": "Fall from height, visible laceration on head, deformity noted. HR 112, BP 125/78, Temp 37.1C.",
            },
        ]
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
