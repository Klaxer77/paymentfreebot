from app.exceptions.base import BaseException
from fastapi import status


class NotificationErrorTypeNotification(BaseException):
    status_code=status.HTTP_400_BAD_REQUEST
    detail="Неверный тип уведомления"

class NotificationDisableALL(BaseException):
    status_code=status.HTTP_200_OK
    detail="Все уведомления отключены"
    
class NotificationOnALL(BaseException):
    status_code=status.HTTP_200_OK
    detail="Все уведомления включены"
    
    
class NotificationOnCreate(BaseException):
    status_code=status.HTTP_200_OK
    detail="Уведомления о новой сделке включены"
    
class NotificationDisableCreate(BaseException):
    status_code=status.HTTP_200_OK
    detail="Уведомления о новой сделке выключены"
    
class NotificationDisableCanceled(BaseException):
    status_code=status.HTTP_200_OK
    detail="Уведомления об отмененных сделках выключены"
    
class NotificationOnCanceled(BaseException):
    status_code=status.HTTP_200_OK
    detail="Уведомления об отмененных сделках включены"
    
class NotificationOnAccept(BaseException):
    status_code=status.HTTP_200_OK
    detail="Уведомления о принятых сделках включены"
    
class NotificationDisableAccept(BaseException):
    status_code=status.HTTP_200_OK
    detail="Уведомления о принятых сделках выключены"

class NotificationDisableConditionsAreMet(BaseException):
    status_code=status.HTTP_200_OK
    detail="Уведомления о завершенных сделках выключены"
    
class NotificationOnConditionsAreMet(BaseException):
    status_code=status.HTTP_200_OK
    detail="Уведомления о завершенных сделках включены"