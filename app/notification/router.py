from fastapi import APIRouter, Depends

from app.exceptions.notification.exception import NotificationDisableALL, NotificationDisableAccept, NotificationDisableCanceled, NotificationDisableConditionsAreMet, NotificationDisableCreate, NotificationErrorTypeNotification, NotificationOnALL, NotificationOnAccept, NotificationOnCanceled, NotificationOnConditionsAreMet, NotificationOnCreate
from app.exceptions.schemas import SExceptionsINFO
from app.notification.dao import NotificationDAO
from app.notification.schemas import SNotification, SNotificationOne
from app.users.depencies import get_current_user
from app.users.schemas import SUser

router = APIRouter(prefix="/notification", tags=["Notifications"])

@router.post("/disable_or_on_all")
async def disable_or_on_all(notif: SNotification, user: SUser = Depends(get_current_user)) -> SExceptionsINFO:
    """
    **Включить или выключить все уведомления**
    
    **Args**
    
    `action` - действие , которое нужно совершить,  только _true_ или _false_
    
    - true - включить
     
    - false - выключить
    
    **Returns**
    
    Возвращает информацию об уведомлении
    """
    await NotificationDAO.update_notification(user_id=user.id, action=notif.action)
    if notif.action == True:
        raise NotificationOnALL
    raise NotificationDisableALL

@router.post("/disable_or_on_one")
async def disable_or_on_one(notif: SNotificationOne, user: SUser = Depends(get_current_user)) -> SExceptionsINFO | None:
    """
    **Включить или выключить уведомления по его типу**
    
    **Args**
    
    `action` - действие , которое нужно совершить,  только _true_ или _false_
    
    - true - включить
     
    - false - выключить
    
    `type_notification` - тип уведомления
    - create - уведомления о созданных сделках
    - canceled - уведомления об отмененных сделках
    - accept - уведомления о принятых сделках
    - conditions_are_met - уведомления о завершенных сделках
    
    **Returns**
    
    Возвращает информацию об уведомлении
    """
    await NotificationDAO.update_notification_one(
        user_id=user.id, 
        type_notification=notif.type_notification,
        action=notif.action
    )
    notification_exceptions = {
    (True, "create"): NotificationOnCreate,
    (False, "create"): NotificationDisableCreate,
    (True, "canceled"): NotificationOnCanceled,
    (False, "canceled"): NotificationDisableCanceled,
    (True, "accept"): NotificationOnAccept,
    (False, "accept"): NotificationDisableAccept,
    (True, "conditions_are_met"): NotificationOnConditionsAreMet,
    (False, "conditions_are_met"): NotificationDisableConditionsAreMet
    }
    raise notification_exceptions[(notif.action, notif.type_notification)]
    