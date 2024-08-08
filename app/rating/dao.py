from app.database import async_session_maker
from sqlalchemy import and_, func, insert, or_, select, update
from app.dao.base import BaseDAO
from app.rating.models import Ratings

class RatingDAO(BaseDAO):
    model = Ratings
    

