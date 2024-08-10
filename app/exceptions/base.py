from fastapi import HTTPException, status


class BaseException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)
        
class ServerError(BaseException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Ошибка сервера"
    
class TelegramError(HTTPException):
    
    def __init__(self, error):
        status_code = status.HTTP_400_BAD_REQUEST
        detail = error
        super().__init__(status_code=status_code, detail=detail)
