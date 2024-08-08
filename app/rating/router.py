from decimal import Decimal
from uuid import UUID
from fastapi import APIRouter, Depends

from app.exceptions.schemas import SExceptionsINFO
from app.rating.dao import RatingDAO
from app.rating.schemas import SRatingCreate
from app.users.dao import UsersDAO
from app.users.depencies import get_current_user
from app.users.schemas import SUser
from app.exceptions.users.exceptions import UserNotFound
from app.logger import logger

router = APIRouter(prefix="/rating", tags=["Rating"])



async def get_rating(user_id: UUID):
    ratings = await RatingDAO.find_one_or_none(rated_user_id=user_id)
    average_rating = round(float(sum(rating.score for rating in ratings)) / len(ratings), 2)
    return {"rating": average_rating}

    
