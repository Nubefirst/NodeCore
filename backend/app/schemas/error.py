from pydantic import BaseModel


class Error(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: Error
