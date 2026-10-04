from fastapi import APIRouter, Depends, HTTPException

from config.db_conf import get_db
from crud import users as users_crud
from models.users import User
from schemas.users import (
    UserAuthResponse,
    UserChangePassword,
    UserCreate,
    UserInfoResponse,
    UserUpdate,
)
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/user", tags=["用户模块"])


@router.post("/register", summary="用户注册")
async def register(user_data: UserCreate, db=Depends(get_db)):
    # 校验用户名、邮箱是否已存在
    if await users_crud.get_user_by_username(db, user_data.username):
        raise HTTPException(status_code=400, detail="用户名已存在")
    if await users_crud.get_user_by_email(db, user_data.email):
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    user = await users_crud.create_user(db, user_data)
    token = await users_crud.create_token(db, user.id)

    response_data = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(user))
    return success_response(message="注册成功", data=response_data)


@router.post("/login", summary="用户登录")
async def login(user_data: UserCreate, db=Depends(get_db)):
    user = await users_crud.authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = await users_crud.create_token(db, user.id)
    response_data = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(user))
    return success_response(message="登录成功", data=response_data)


@router.get("/info", summary="获取当前用户信息")
async def get_user_info(user: User = Depends(get_current_user)):
    return success_response(message="获取用户信息成功", data=UserInfoResponse.model_validate(user))


@router.put("/update", summary="修改用户信息")
async def update_user_info(
    user_data: UserUpdate,
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    user = await users_crud.update_user(db, user, user_data)
    return success_response(message="更新用户信息成功", data=UserInfoResponse.model_validate(user))


@router.put("/password", summary="修改用户密码")
async def update_password(
    password_data: UserChangePassword,
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    ok = await users_crud.change_password(db, user, password_data.old_password, password_data.new_password)
    if not ok:
        raise HTTPException(status_code=400, detail="原密码错误")
    return success_response(message="修改密码成功")
