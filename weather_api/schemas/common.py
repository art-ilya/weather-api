from pydantic import BaseModel


class HTTPError(BaseModel):
    detail: str

    class Config:
        schema_extra = {
            "example": {"detail": "HTTPException raised."},
        }


responses = {
    400: {"model": HTTPError, "description": "Bad request"},
    422: {"model": HTTPError, "description": "Validation error"},
    503: {"model": HTTPError, "description": "Service Unavailable"},
}
