from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.dependencies import get_current_user
from app.core.constants.general import RouteSettings
from app.core.logging_config import firelog
from app.core.schemas.response_schemas import GenericAPIResponse
from app.db.session import SessionDependency
from app.users.constants import (
    UserEndpoints,
    UserHttpErrorDetails,
    UserLoggingStrings,
    UserSuccessMessages,
)
from app.users.models.user_model import User
from app.users.schemas.user_schema import (
    UserCompleteProfile,
    UserPublic,
    UsersPublic,
    UserUpdate,
)
from app.users.services.user_service import UserService

router = APIRouter()


@router.patch(
    UserEndpoints.COMPLETE_PROFILE,
    summary="Complete profile for the current user.",
    response_description="The updated user profile.",
    response_model=GenericAPIResponse[UserPublic],
)
def complete_current_user_profile(
    profile_data: UserCompleteProfile,
    session: SessionDependency,
    current_user: User = Depends(get_current_user),  # noqa: B008
    user_service: UserService = Depends(UserService),  # noqa: B008
) -> GenericAPIResponse[UserPublic]:
    """
    Allows the currently authenticated user to complete their profile.

    This endpoint is typically used after initial registration (e.g., via OTP)
    to provide essential profile details like name, email, and date of birth.
    It can only be called if the user's profile is not already marked as complete.
    """
    firelog.info(
        UserLoggingStrings.REQUEST_COMPLETE_PROFILE_TEMPLATE.format(
            user_id=current_user.id
        )
    )
    if current_user.is_profile_complete:
        firelog.warning(
            UserLoggingStrings.PROFILE_ALREADY_COMPLETE_TEMPLATE.format(
                user_id=current_user.id
            )
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=UserHttpErrorDetails.PROFILE_ALREADY_COMPLETE,
        )

    updated_user = user_service.complete_user_profile(
        db=session, user_to_update=current_user, profile_in=profile_data
    )
    user_data_payload = UserPublic.model_validate(updated_user)

    firelog.info(
        UserLoggingStrings.PROFILE_COMPLETED_SUCCESS_TEMPLATE.format(
            user_id=current_user.id
        )
    )
    return GenericAPIResponse.success_response(
        data_payload=user_data_payload, msg=UserSuccessMessages.PROFILE_COMPLETED
    )


@router.get(
    UserEndpoints.ROOT,
    summary="List all users (Superuser only).",
    response_description="A list of users with pagination count.",
    response_model=GenericAPIResponse[UsersPublic],
)
def read_users(
    session: SessionDependency,
    current_user: User = Depends(get_current_user),  # noqa: B008
    user_service: UserService = Depends(UserService),  # noqa: B008
    skip: int = Query(
        RouteSettings.DEFAULT_SKIP,
        ge=0,
        description="Number of records to skip for pagination.",
    ),
    limit: int = Query(
        RouteSettings.DEFAULT_LIMIT,
        ge=1,
        le=RouteSettings.MAX_LIMIT,
        description="Maximum number of records to return.",
    ),
) -> GenericAPIResponse[UsersPublic]:
    """
    Retrieve a paginated list of users.

    Requires **superuser privileges**.
    """
    firelog.info(
        UserLoggingStrings.LIST_USERS_REQUEST_TEMPLATE.format(
            user_id=current_user.id, skip=skip, limit=limit
        )
    )
    if not current_user.is_superuser:
        firelog.warning(
            UserLoggingStrings.FORBIDDEN_TEMPLATE.format(
                current_user_id=current_user.id,
                action_description="list all users",
                target_user_id="N/A",
            )
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=UserHttpErrorDetails.FORBIDDEN_ACCESS_RESOURCE,
        )

    users_public_data = user_service.get_users(db=session, skip=skip, limit=limit)

    firelog.info(
        UserLoggingStrings.USERS_LISTED_TEMPLATE.format(
            count=users_public_data.count, user_id=current_user.id
        )
    )
    return GenericAPIResponse.success_response(
        data_payload=users_public_data, msg=UserSuccessMessages.USERS_RETRIEVED
    )


@router.get(
    UserEndpoints.ME,
    summary="Get current authenticated user's details.",
    response_description="Details of the currently logged-in user.",
    response_model=GenericAPIResponse[UserPublic],
)
def read_user_me(
    current_user: User = Depends(get_current_user),  # noqa: B008
) -> GenericAPIResponse[UserPublic]:
    """
    Fetch the complete profile information for the currently authenticated user.
    """
    firelog.info(
        UserLoggingStrings.GET_ME_REQUEST_TEMPLATE.format(user_id=current_user.id)
    )
    user_data_payload = UserPublic.model_validate(current_user)
    firelog.info(
        UserLoggingStrings.GET_ME_SUCCESS_TEMPLATE.format(user_id=current_user.id)
    )
    return GenericAPIResponse.success_response(
        data_payload=user_data_payload, msg=UserSuccessMessages.CURRENT_USER_RETRIEVED
    )


@router.get(
    UserEndpoints.USER_BY_ID,
    summary="Get a specific user by their ID.",
    response_description="Details of the specified user.",
    response_model=GenericAPIResponse[UserPublic],
)
def read_user_by_id(
    user_id: int,
    session: SessionDependency,
    current_user: User = Depends(get_current_user),  # noqa: B008
    user_service: UserService = Depends(UserService),  # noqa: B008
) -> GenericAPIResponse[UserPublic]:
    """
    Retrieve information for a specific user by their unique ID.

    - Authenticated users can retrieve their own information.
    - **Superusers** can retrieve information for any user.
    """
    firelog.info(
        UserLoggingStrings.GET_USER_BY_ID_REQUEST_TEMPLATE.format(
            current_user_id=current_user.id, target_user_id=user_id
        )
    )
    if user_id != current_user.id and not current_user.is_superuser:
        firelog.warning(
            UserLoggingStrings.FORBIDDEN_TEMPLATE.format(
                current_user_id=current_user.id,
                action_description="view user details",
                target_user_id=user_id,
            )
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=UserHttpErrorDetails.FORBIDDEN_VIEW_USER,
        )

    user = user_service.get_user_by_id(db=session, user_id=user_id)
    if not user:
        firelog.warning(
            UserLoggingStrings.USER_NOT_FOUND_TEMPLATE.format(
                user_id=user_id, action="retrieving"
            )
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=UserHttpErrorDetails.USER_NOT_FOUND_TEMPLATE.format(user_id=user_id),
        )

    user_data_payload = UserPublic.model_validate(user)
    firelog.info(
        UserLoggingStrings.GET_USER_BY_ID_SUCCESS_TEMPLATE.format(
            target_user_id=user_id
        )
    )
    return GenericAPIResponse.success_response(
        data_payload=user_data_payload,
        msg=UserSuccessMessages.USER_BY_ID_RETRIEVED_TEMPLATE.format(user_id=user_id),
    )


@router.patch(
    UserEndpoints.USER_BY_ID,
    summary="Update a specific user's information.",
    response_description="The updated user details.",
    response_model=GenericAPIResponse[UserPublic],
)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    session: SessionDependency,
    current_user: User = Depends(get_current_user),  # noqa: B008
    user_service: UserService = Depends(UserService),  # noqa: B008
) -> GenericAPIResponse[UserPublic]:
    """
    Update attributes for a specific user.

    - Authenticated users can update their own information.
    - **Superusers** can update information for any user.
    - Only fields present in the request body will be updated.
    """
    firelog.info(
        UserLoggingStrings.UPDATE_USER_REQUEST_TEMPLATE.format(
            current_user_id=current_user.id, target_user_id=user_id
        )
    )
    if user_id != current_user.id and not current_user.is_superuser:
        firelog.warning(
            UserLoggingStrings.FORBIDDEN_TEMPLATE.format(
                current_user_id=current_user.id,
                action_description="update user",
                target_user_id=user_id,
            )
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=UserHttpErrorDetails.FORBIDDEN_UPDATE_USER,
        )

    updated_user = user_service.update_user_details(
        db=session,
        user_id_to_update=user_id,
        user_in=user_in,
        current_user=current_user,
    )
    if not updated_user:
        firelog.warning(
            UserLoggingStrings.USER_NOT_FOUND_TEMPLATE.format(
                user_id=user_id, action="updating"
            )
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=UserHttpErrorDetails.USER_NOT_FOUND_TEMPLATE.format(user_id=user_id),
        )

    user_data_payload = UserPublic.model_validate(updated_user)
    firelog.info(
        UserLoggingStrings.USER_UPDATED_SUCCESS_TEMPLATE.format(target_user_id=user_id)
    )
    return GenericAPIResponse.success_response(
        data_payload=user_data_payload,
        msg=UserSuccessMessages.USER_UPDATED_TEMPLATE.format(user_id=user_id),
    )


@router.delete(
    UserEndpoints.USER_BY_ID,
    summary="Delete a user.",
    response_description="No content returned on successful deletion.",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(
    user_id: int,
    session: SessionDependency,
    current_user: User = Depends(get_current_user),  # noqa: B008
    user_service: UserService = Depends(UserService),  # noqa: B008
) -> None:
    """
    Delete a specific user by their ID.

    - Authenticated users can delete their own account.
    - **Superusers** can delete any user account (behavior for superuser deleting self might be restricted in the service layer).
    - This operation is irreversible.
    """
    firelog.info(
        UserLoggingStrings.DELETE_USER_REQUEST_TEMPLATE.format(
            current_user_id=current_user.id, target_user_id=user_id
        )
    )

    deleted = user_service.remove_user(
        db=session, user_id_to_delete=user_id, current_user=current_user
    )
    if not deleted:
        # This case means the user wasn't found, which the service handles by returning False.
        firelog.warning(
            UserLoggingStrings.USER_NOT_FOUND_TEMPLATE.format(
                user_id=user_id, action="deleting"
            )
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=UserHttpErrorDetails.USER_DELETE_NOT_FOUND_BY_REPO.format(
                user_id=user_id
            ),
        )
    firelog.info(
        UserLoggingStrings.USER_DELETED_SUCCESS_TEMPLATE.format(target_user_id=user_id)
    )
    return
