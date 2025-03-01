from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.exc import NoResultFound
from starlette import status

from src.database.base import SessionDep
from src.users.services.selectors import user_filter_by_token

oauth2_scheme = HTTPBearer()


async def get_current_user(
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
):
    try:
        return await user_filter_by_token(session, credentials.credentials)
    except (ValueError, jwt.PyJWTError, NoResultFound) as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error))


CurrentUserDep = Annotated['User', Depends(get_current_user)]
