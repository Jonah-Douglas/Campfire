from sqlmodel import SQLModel


# Tokens
## JSON payload containing the access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"

## JWToken contents
class TokenPayload(SQLModel):
    sub: int | None = None