from fastapi import APIRouter, Depends, HTTPException, status, Query,Body
from sqlalchemy.orm import Session 
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Any
import uuid 
from utils.logger import logger
from core.database import get_session
from resources.users.validation.user import UserCreate, UserUpdate, User as UserSchema
from resources.users.apis.user_api import UserService

class UserRouter:
    def __init__(self):
        self.router = APIRouter()
        self.router.post("/createUser", response_model=UserSchema)(self.create_user) 
        self.router.post("/inserUsers",response_model=List[Any])(self.insert_users)
        self.router.get("/getUser", response_model=UserSchema)(self.read_user)
        self.router.get("/getAllUsers", response_model=List[UserSchema])(self.read_users)
        self.router.put("/updateUser", response_model=UserSchema)(self.update_user)
        self.router.delete("/deleteUser", response_model=UserSchema)(self.delete_user) 

    
    async def insert_users(self, db: Session = Depends(get_session)):
        service = UserService(db)
        result = await service.insert_users() 
        if result is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching users")
        return result

    async def create_user(self, user: UserCreate = Body(...), db: Session = Depends(get_session)): 
        crud = UserService(db)
        db_user = crud.create_user(user)
        if db_user is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email, username, or mobile number already registered")
        return db_user

    async def read_user(self, user_id: uuid.UUID = Query(...), db: Session = Depends(get_session)):
        try:
            service = UserService(db)
            db_user = service.get_user(user_id)
            if db_user is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            return db_user
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
         

    async def read_users(self, skip: int = 0, limit: int = 10, db: Session = Depends(get_session)):
        crud = UserService(db)
        users = crud.get_all_users()
        return users

    async def update_user(self, user_id: uuid.UUID = Query(...), user: UserUpdate = Body(...), db: Session = Depends(get_session)):
        crud = UserService(db)
        db_user = crud.update_user(user_id, user)
        if db_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return db_user

    async def delete_user(self, user_id: uuid.UUID = Query(...), db: Session = Depends(get_session)):
        crud = UserService(db)
        db_user = crud.delete_user(user_id)
        if db_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return db_user

user_router = UserRouter().router
