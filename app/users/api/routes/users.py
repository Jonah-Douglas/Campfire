from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.dependencies import get_current_user
from app.core.constants.general import RouteSettings
from app.core.logging.logger_wrapper import firelog
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
    """
    log_extra_request = {"user_id": current_user.id}
    firelog.info(
        UserLoggingStrings.REQUEST_COMPLETE_PROFILE_TEMPLATE, extra=log_extra_request
    )

    if current_user.is_profile_complete:
        firelog.warning(
            UserLoggingStrings.PROFILE_ALREADY_COMPLETE_TEMPLATE,
            extra=log_extra_request,
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
        UserLoggingStrings.PROFILE_COMPLETED_SUCCESS_TEMPLATE,
        extra=log_extra_request,
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
    skip: int = Query(RouteSettings.DEFAULT_SKIP, ge=0),
    limit: int = Query(RouteSettings.DEFAULT_LIMIT, ge=1, le=RouteSettings.MAX_LIMIT),
) -> GenericAPIResponse[UsersPublic]:
    """
    Retrieve a paginated list of users. Requires superuser privileges.
    """
    log_extra_list_request = {"user_id": current_user.id, "skip": skip, "limit": limit}
    firelog.info(
        UserLoggingStrings.LIST_USERS_REQUEST_TEMPLATE, extra=log_extra_list_request
    )

    if not current_user.is_superuser:
        log_extra_forbidden = {
            "current_user_id": current_user.id,
            "action_description": "list all users",
            "target_user_id": "N/A",
        }
        firelog.warning(
            UserLoggingStrings.FORBIDDEN_TEMPLATE, extra=log_extra_forbidden
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=UserHttpErrorDetails.FORBIDDEN_ACCESS_RESOURCE,
        )

    users_public_data = user_service.get_users(db=session, skip=skip, limit=limit)

    log_extra_listed = {"count": users_public_data.count, "user_id": current_user.id}
    firelog.info(UserLoggingStrings.USERS_LISTED_TEMPLATE, extra=log_extra_listed)
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
    log_extra_me = {"user_id": current_user.id}
    firelog.info(UserLoggingStrings.GET_ME_REQUEST_TEMPLATE, extra=log_extra_me)

    user_data_payload = UserPublic.model_validate(current_user)
    firelog.info(
        UserLoggingStrings.GET_ME_SUCCESS_TEMPLATE,
        extra=log_extra_me,
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
    """
    log_extra_get_by_id_req = {
        "current_user_id": current_user.id,
        "target_user_id": user_id,
    }
    firelog.info(
        UserLoggingStrings.GET_USER_BY_ID_REQUEST_TEMPLATE,
        extra=log_extra_get_by_id_req,
    )

    if user_id != current_user.id and not current_user.is_superuser:
        log_extra_forbidden = {
            "current_user_id": current_user.id,
            "action_description": "view user details",
            "target_user_id": user_id,
        }
        firelog.warning(
            UserLoggingStrings.FORBIDDEN_TEMPLATE, extra=log_extra_forbidden
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=UserHttpErrorDetails.FORBIDDEN_VIEW_USER,
        )

    user = user_service.get_user_by_id(db=session, user_id=user_id)
    if not user:
        log_extra_not_found = {
            "user_id": user_id,
        }
        firelog.warning(
            UserHttpErrorDetails.USER_NOT_FOUND_TEMPLATE, extra=log_extra_not_found
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=UserHttpErrorDetails.USER_NOT_FOUND_TEMPLATE % user_id,
        )

    user_data_payload = UserPublic.model_validate(user)
    log_extra_get_by_id_success = {"target_user_id": user_id}
    firelog.info(
        UserLoggingStrings.GET_USER_BY_ID_SUCCESS_TEMPLATE,
        extra=log_extra_get_by_id_success,
    )
    return GenericAPIResponse.success_response(
        data_payload=user_data_payload,
        msg=UserSuccessMessages.USER_BY_ID_RETRIEVED_TEMPLATE % user_id,
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
    """
    log_extra_update_req = {
        "current_user_id": current_user.id,
        "target_user_id": user_id,
    }
    firelog.info(
        UserLoggingStrings.UPDATE_USER_REQUEST_TEMPLATE, extra=log_extra_update_req
    )

    if user_id != current_user.id and not current_user.is_superuser:
        log_extra_forbidden = {
            "current_user_id": current_user.id,
            "action_description": "update user",
            "target_user_id": user_id,
        }
        firelog.warning(
            UserLoggingStrings.FORBIDDEN_TEMPLATE, extra=log_extra_forbidden
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
        log_extra_not_found = {
            "user_id": user_id,
        }
        firelog.warning(
            UserHttpErrorDetails.USER_NOT_FOUND_TEMPLATE, extra=log_extra_not_found
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=UserHttpErrorDetails.USER_NOT_FOUND_TEMPLATE % user_id,
        )

    user_data_payload = UserPublic.model_validate(updated_user)
    log_extra_update_success = {"target_user_id": user_id}
    firelog.info(
        UserLoggingStrings.USER_UPDATED_SUCCESS_TEMPLATE, extra=log_extra_update_success
    )
    return GenericAPIResponse.success_response(
        data_payload=user_data_payload,
        msg=UserSuccessMessages.USER_UPDATED_TEMPLATE % user_id,
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
    """
    log_extra_delete_req = {
        "current_user_id": current_user.id,
        "target_user_id": user_id,
    }
    firelog.info(
        UserLoggingStrings.DELETE_USER_REQUEST_TEMPLATE, extra=log_extra_delete_req
    )

    deleted = user_service.remove_user(
        db=session, user_id_to_delete=user_id, current_user=current_user
    )
    if not deleted:
        log_extra_not_found = {
            "user_id": user_id,
        }
        firelog.warning(
            UserHttpErrorDetails.USER_NOT_FOUND_TEMPLATE, extra=log_extra_not_found
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=UserHttpErrorDetails.USER_DELETE_NOT_FOUND_BY_REPO.format(
                user_id=user_id
            ),
        )

    log_extra_delete_success = {"target_user_id": user_id}
    firelog.info(
        UserLoggingStrings.USER_DELETED_SUCCESS_TEMPLATE, extra=log_extra_delete_success
    )
    return None
