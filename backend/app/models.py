from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field, model_validator

VALID_CATEGORIES = {"感情", "事业", "财运", "学业", "合作", "健康", "寻物", "其他"}


class CreateDivinationRequest(BaseModel):
    question: str = Field(..., min_length=1)
    category: str = Field(default="其他")
    timeframe: Optional[str] = None
    session_token: str

    @model_validator(mode="after")
    def validate_category(self) -> CreateDivinationRequest:
        if self.category not in VALID_CATEGORIES:
            raise ValueError(f"category must be one of {sorted(VALID_CATEGORIES)}")
        return self


class DivinationCreatedResponse(BaseModel):
    divination_id: str


class SubmitLineRequest(BaseModel):
    line_number: int = Field(..., ge=1, le=6)
    coin_values: list[int] = Field(..., min_length=3, max_length=3)

    @model_validator(mode="after")
    def validate_coins(self) -> SubmitLineRequest:
        for v in self.coin_values:
            if v not in (2, 3):
                raise ValueError(f"Each coin value must be 2 (tails) or 3 (heads), got {v}")
        return self


class LineRecord(BaseModel):
    line_number: int
    coin_values: list[int]
    coin_sum: int
    line_type: str
    is_changing: bool


class LineResultResponse(BaseModel):
    line_number: int
    coin_values: list[int]
    coin_sum: int
    line_type: str
    is_changing: bool


class DivinationResultResponse(BaseModel):
    divination_id: str
    question: str
    category: str
    timeframe: Optional[str]
    base_hexagram: Optional[int]
    changed_hexagram: Optional[int]
    changing_lines: list[int]
    lines: list[LineRecord]
    base_hexagram_data: Optional[dict]
    changed_hexagram_data: Optional[dict]


class InterpretationResponse(BaseModel):
    divination_id: str
    summary: Optional[str] = None
    base_reading: Optional[str] = None
    changing_lines_analysis: Optional[str] = None
    changed_hexagram_trend: Optional[str] = None
    category_advice: Optional[str] = None
    action_advice: Optional[list[str]] = None
    generated_by: str = "ai"
    provider: Optional[str] = None
    error: Optional[str] = None


class FollowupMessageRequest(BaseModel):
    message: str = Field(..., min_length=1)


class FollowupSendResponse(BaseModel):
    content: str
    source_note: str
    rounds_used: int
    rounds_limit: int


class MessageRecord(BaseModel):
    role: str
    content: str
    created_at: str


class FollowupHistoryResponse(BaseModel):
    messages: list[MessageRecord]
    rounds_used: int
    rounds_limit: int
