from pydantic import BaseModel, ConfigDict, Field


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str