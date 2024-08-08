from pydantic import BaseModel, field_validator
from uuid import UUID

from app.exceptions.rating.exception import RatingScoreError

class SRatingCreate(BaseModel):
    rated_user_id: UUID
    score: int
    
    @field_validator("score")
    @classmethod
    def check_score(cls, v: int):
        if v < 1 or v > 5:
            raise RatingScoreError
        return v
