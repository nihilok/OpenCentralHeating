import time
from fastapi import Depends, status, APIRouter
from starlette.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import json
from ..secrets.constants import (
    SECRET_KEY,
    ALGORITHM,
    GUEST_IDS,
    SUPERUSERS,
    ACCESS_TOKEN_EXPIRE_DAYS,
)
from ..models import (
    HouseholdMember,
    HouseholdMemberPydantic,
    HouseholdMemberPydanticIn,
    PasswordChange,
)
from ..logger import get_logger

logger = get_logger(__name__)
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(password, hash):
    return pwd_context.verify(password, hash)


async def authenticate_user(
    username: str, password: str
) -> Optional[HouseholdMemberPydantic]:
    user = await HouseholdMemberPydantic.from_queryset_single(
        HouseholdMember.get(name=username)
    )
    try:
        if not verify_password(password, user.password_hash):
            return False
        return user
    except Exception:
        return None


def create_access_token(data: dict):
    to_encode = data.copy()
    expires_delta = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug(f'TOKEN DATA: {json.dumps(decoded_token)}')
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except Exception:
        return {"message": "token expired, please log in again"}


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await HouseholdMemberPydantic.from_queryset_single(
        HouseholdMember.get(name=token_data.username)
    )
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: HouseholdMember = Depends(get_current_user),
):
    if current_user.id in GUEST_IDS:
        raise credentials_exception
    return current_user


@router.post("/token/", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    print(form_data.username + " logging in")
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(data={"sub": user.name})
    return Token(access_token=access_token, token_type="bearer")


@router.get("/check_token/")
async def check_token(
    user: HouseholdMemberPydantic = Depends(get_current_user),
):
    access_token = create_access_token(data={"sub": user.name})
    return Token(access_token=access_token, token_type="bearer")


async def check_superuser(
    user: HouseholdMemberPydantic = Depends(get_current_user),
) -> Optional[HouseholdMemberPydantic]:
    if user.id in SUPERUSERS:
        return user


@router.post("/users/")
async def create_user(
    user: HouseholdMemberPydanticIn,
    superuser: HouseholdMemberPydantic = Depends(check_superuser),
):
    if superuser:
        user_obj = HouseholdMember(
            name=user.name,
            password_hash=get_password_hash(user.password_hash),
            household_id=1,
        )
        await user_obj.save()
        return await HouseholdMemberPydantic.from_tortoise_orm(user_obj)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You need to be a superuser to create another user.",
        )


@router.post("/password_change/")
async def change_password(
    body: PasswordChange,
    user: HouseholdMemberPydantic = Depends(get_current_active_user),
):
    user = await HouseholdMember.get(id=user.id)
    if not user.verify_password(body.current_password):
        raise HTTPException(status_code=401)
    if not body.new_password == body.password_check:
        raise HTTPException(status_code=422)
    user.password_hash = get_password_hash(body.new_password)
    return {"message": "Password changed"}
