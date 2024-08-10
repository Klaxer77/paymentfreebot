from fastapi import status

from app.exceptions.base import BaseException



class TransactionNotFound(BaseException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Такой сделки не существует"


class TransactionStatusCanceled(BaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Сделка уже была отменена"


class TransactionStatusCanceledTrue(BaseException):
    status_code = status.HTTP_200_OK
    detail = "Сделка отменена"


class TransactionStatusСompleted(BaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Сделка уже была завершена"


class TransactionStatusActive(BaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Сделка уже активна"


class TransactionStatusActiveTrue(BaseException):
    status_code = status.HTTP_201_CREATED
    detail = "Сделка принята"


class TransactionStatusPending(BaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Сделка еще не была принята"


class TransactionСonditionsAreMet(BaseException):
    status_code = status.HTTP_200_OK
    detail = "Сделка успешно завершена"


class TransactionExceedsBalance(BaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Сумма сделки превышает текущий баланс"


class TransactionUserError(BaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Сделка с самим собой не возможна"


class TransactionLimitBalance(BaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Текущий баланс будет составлять меньше, чем сумма всех поданых заявок на сделки. Пополните баланс или уменьшите сумму сделки"


class TransactionCreated(BaseException):
    status_code = status.HTTP_201_CREATED
    detail = "Сделка создана"


class TransactionNotTheInitiator(BaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Вы не являетесь инициатором сделки"


class TransactionErrorInitiator(BaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Принять завку на сделку может только получатель"
    
class TransactionErrorInitiatorOrUserFor(BaseException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Вы не являетесь участником сделки"
    
    
    
