from sqlmodel import SQLModel


# Messages
## Generic model for returning message response
class Message(SQLModel):
    message: str