from app.exceptions.base import BaseException
from fastapi import status

class UserNotFound(BaseException):
    status_code=status.HTTP_404_NOT_FOUND
    detail="Пользователь не найден"
    
class TokenExpiredException(BaseException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Token has expired"

# class InvalidCredentialsException(BaseException):
#     status_code=status.HTTP_401_UNAUTHORIZED
#     detail="Invalid username or password"
    
class NoneToken(BaseException):   
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Токен отсутствует'
    
class InvalidTokenException(BaseException):   
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Неверный токен"
    
class UserISerror(BaseException):     
    status_code=status.HTTP_409_CONFLICT
    detail='Такой пользователь не существует или введенный пароль неверный'
    
class UserISexists(BaseException):      
    status_code=status.HTTP_409_CONFLICT
    detail='Пользователь с таким username уже существует'
    
class UserCheckAdminRole(BaseException):
    status_code=status.HTTP_403_FORBIDDEN
    detail='Недостаточно прав'
    
class TokenExpiredException(BaseException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Срок действия токена истек"
    
class IncorrectTokenFormatException(BaseException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Неверный формат токена"
    
class IncorrectTokenHeaders(BaseException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Отсутсвует токен в заголовке"
    
class UserIsNotPresentException(BaseException):
    status_code=status.HTTP_401_UNAUTHORIZED