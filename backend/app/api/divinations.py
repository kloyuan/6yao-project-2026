from fastapi import APIRouter, Depends
from supabase import Client

from app.db import get_supabase
from app.models import (
    CreateDivinationRequest,
    DivinationCreatedResponse,
    SubmitLineRequest,
    LineResultResponse,
    DivinationResultResponse,
)
from app.services import divination_service

router = APIRouter()


@router.post("", response_model=DivinationCreatedResponse)
def create_divination(
    body: CreateDivinationRequest,
    db: Client = Depends(get_supabase),
):
    divination_id = divination_service.create_divination(body, db)
    return {"divination_id": divination_id}


@router.post("/{divination_id}/lines", response_model=LineResultResponse)
def submit_line(
    divination_id: str,
    body: SubmitLineRequest,
    db: Client = Depends(get_supabase),
):
    return divination_service.submit_line(
        divination_id, body.line_number, body.coin_values, db,
        cast_datetime=body.cast_datetime,
        timezone=body.timezone,
    )


@router.get("/{divination_id}/result", response_model=DivinationResultResponse)
def get_result(divination_id: str, db: Client = Depends(get_supabase)):
    return divination_service.get_result(divination_id, db)
