from fastapi import APIRouter, Depends
from supabase import Client

from app.db import get_supabase
from app.models import InterpretationResponse
from app.services import interpretation_service

router = APIRouter()


@router.post("/{divination_id}/interpret", response_model=InterpretationResponse)
def interpret(divination_id: str, db: Client = Depends(get_supabase)):
    return interpretation_service.get_or_create_interpretation(divination_id, db)
