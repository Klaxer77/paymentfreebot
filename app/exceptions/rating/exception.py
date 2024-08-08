from fastapi import status

from app.exceptions.base import BaseException


class RatingScoreError(BaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Рейтинг должен быть от 1 до 5"