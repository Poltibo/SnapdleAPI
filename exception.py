import abc
from enum import Enum
from pydantic import BaseModel, Field


class ApplicationException(Exception, metaclass=abc.ABCMeta):

    @property
    @abc.abstractmethod
    def message(self) -> str:
        """Message to detail what happened"""

    def __str__(self):
        return self.message


class CardNotFoundException(ApplicationException):
    def __init__(self, card_name: str):
        self.card_name = card_name

    @property
    def message(self) -> str:
        return f"Card '{self.card_name}' not found in the database"


class ApiMessageCode(str, Enum):
    CARD_NAME_NOT_FOUND = "CARD_NAME_NOT_FOUND"

    INVALID_INPUT = "INVALID_INPUT"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"


class APIMessage(BaseModel):
    """Structure of errors responses"""

    code: ApiMessageCode = Field(..., description="Textual code of the error")

    message: str = Field(..., description="Human readable explanation of the error")

    correlationId: str = Field(..., description="Unique reference to the request which return this error")
