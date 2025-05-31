from typing import Annotated
from fastapi import APIRouter, Depends, Request, status, Body
from fastapi.security import OAuth2PasswordRequestForm

# Application-specific imports
from app.api.dependencies import SessionDependency, CurrentUser
from app.models.token import Token
from app.services.auth_service import AuthService


router = APIRouter()

# JD TODO: Consider adding a deny list to handle invalidating refresh tokens, which handles setting a token that was valid as an actively disallowed token while generating a new one
# JD TODO: When setting to prod, make sure to use https to guarantee safety when passing plaintext user and passwords to this resource
@router.post(
    "/login",
    summary="Log in user and return access and refresh tokens",
    status_code=status.HTTP_200_OK,
)
def login_access_token(
    session: SessionDependency,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    request: Request, # Inject the request object
    current_auth_service: AuthService = Depends(AuthService)
) -> Token:
    """
    Log in the user by validating their username and password.

    The client application is responsible for saving both the access
    and refresh tokens locally after calling this endpoint.
    """
    # Pass only necessary parts of the request to the service
    _user, token_data = current_auth_service.login_user(
        db=session,
        email=form_data.username,
        password=form_data.password,
        request_headers=dict(request.headers),
        client_host=request.client.host if request.client else None
    )

    return token_data

@router.post(
    "/logout",
    summary="Log out user and invalidate refresh token session",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    *,
    session: SessionDependency,
    current_user: CurrentUser,
    refresh_token: str = Body(..., embed=True, description="The refresh token to invalidate"),
    current_auth_service: AuthService = Depends(AuthService)
):
    """
    Log out the user by invalidating their active refresh token session.

    The client application is responsible for discarding both the access
    and refresh tokens locally after calling this endpoint.
    """
    current_auth_service.logout_user(
        db=session,
        current_user_id=current_user.id,
        refresh_token_to_invalidate=refresh_token
    )

    # FastAPI handles the 204 status code automatically if nothing is returned
    return