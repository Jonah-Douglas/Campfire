from datetime import datetime, timedelta, timezone
from typing import Any, Tuple
from jose import jwt
import bcrypt
from app.core.config import settings
import uuid


ALGORITHM = "HS256"

# Create access token via HS256 encoding
def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "jti": str(uuid.uuid4())
    }
    encoded_jwt = jwt.encode(to_encode, settings.ACCESS_TOKEN_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Create refresh token via HS256 encoding, returning the token and its JTI
def create_refresh_token_with_jti(subject: str | Any, expires_delta: timedelta) -> Tuple[str, str]:
    expire = datetime.now(timezone.utc) + expires_delta
    jti_val = str(uuid.uuid4()) # Generate JTI
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "jti": jti_val # Add the jti claim
    }
    encoded_jwt = jwt.encode(to_encode, settings.REFRESH_TOKEN_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, jti_val # Return both the token and its JTI

# Hashes plaintext password
def get_password_hash(password: str) -> str:
    # Ensure the password is in bytes
    password_bytes = password.encode('utf-8')
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password_bytes = bcrypt.hashpw(password_bytes, salt)
    # Return the hashed password as a string
    return hashed_password_bytes.decode('utf-8')

# Verifies plaintext password against the hashed password stored in the database
def verify_password(plain_password: str, hashed_password_str: str) -> bool:
    # Ensure both are in bytes
    plain_password_bytes = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password_str.encode('utf-8')
    # Check the password
    return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)