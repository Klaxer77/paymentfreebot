from pydantic import BaseModel, field_validator

from app.exceptions.notification.exception import NotificationErrorTypeNotification



class SNotification(BaseModel):
    action: bool
    
class SNotificationOne(BaseModel):
    action: bool
    type_notification: str
    
    @field_validator("type_notification")
    @classmethod
    def check_action(cls, v: str):
        if v not in ["create","canceled","accept","conditions_are_met"]:
            raise NotificationErrorTypeNotification
        return v
    
    
    