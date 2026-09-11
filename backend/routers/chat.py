"""Chat router — natural-language interface routed through AgentOrchestrator."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from schemas.chat import ChatRequest, ChatResponse
from orchestration.orchestrator import orchestrator
from services.profile_service import get_profile, profile_to_dict

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    profile = get_profile(db, request.user_id)
    profile_dict = profile_to_dict(profile) if profile else None

    try:
        result = orchestrator.dispatch(
            message=request.message,
            profile=profile_dict,
            request_type=request.request_type,
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Agent error: {str(exc)}")

    return ChatResponse(
        response=result.get("response", ""),
        agent_used=result.get("agent_used", "unknown"),
        disclaimer=result.get("disclaimer"),
    )
