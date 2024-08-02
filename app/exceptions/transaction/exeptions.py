from app.exceptions.base import BaseException
from fastapi import status

class TransactionStatusCanceled(BaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = ""

    def __init__(self, transaction):
        self.detail = f"Сделка с {transaction.user_for_first_name} уже была отменена"
        super().__init__()
        
class TransactionStatusCanceledTrue(BaseException):
    status_code = status.HTTP_200_OK
    detail = ""

    def __init__(self, transaction):
        self.detail = f"Сделка с {transaction.user_for_first_name} отменена"
        super().__init__()
        
class TransactionStatusСompleted(BaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = ""

    def __init__(self, transaction):
        self.detail = f"Сделка с {transaction.user_for_first_name} уже была завершена"
        super().__init__()
        
class TransactionStatusActive(BaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = ""

    def __init__(self, transaction):
        self.detail = f"Сделка с {transaction.user_for_first_name} уже активна"
        super().__init__()
        
class TransactionStatusActiveTrue(BaseException):
    status_code = status.HTTP_201_CREATED
    detail = ""

    def __init__(self, transaction):
        self.detail = f"Сделка с {transaction.user_for_first_name} принята"
        super().__init__()
        
class TransactionStatusPending(BaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = ""

    def __init__(self, transaction):
        self.detail = f"Сделка с {transaction.user_for_first_name} еще не была принята"
        super().__init__()
        
class TransactionСonditionsAreMet(BaseException):
    status_code = status.HTTP_200_OK
    detail = ""

    def __init__(self, transaction):
        self.detail = f"Сделка с {transaction.user_for_first_name} успешно завершена"
        super().__init__()
        
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