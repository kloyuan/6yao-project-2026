from fastapi import APIRouter, Depends
from supabase import Client

from app.db import get_supabase
from app.models import (
    FollowupMessageRequest,
    FollowupSendResponse,
    FollowupHistoryResponse,
)
from app.services import followup_service

router = APIRouter()


@router.post("/{divination_id}/followup", response_model=FollowupSendResponse)
def send_followup(
    divination_id: str,
    body: FollowupMessageRequest,
    db: Client = Depends(get_supabase),
):
    return followup_service.send_message(divination_id, body.message, db)


@router.get("/{divination_id}/followup", response_model=FollowupHistoryResponse)
def get_followup_history(divination_id: str, db: Client = Depends(get_supabase)):
    return followup_service.get_history(divination_id, db)
