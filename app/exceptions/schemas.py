from pydantic import BaseModel

class SExceptions(BaseModel):
    status: int
    detail: str