from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.user import User
from resources.users.validation.user import UserCreate, UserUpdate
import uuid 
import httpx
from utils.logger import logger

class UserService:
    def __init__(self, db: Session):
        self.db = db   

    async def insert_users(self): 
        url = "https://dummyjson.com/users"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)  
            if response.status_code != 200: 
               return None 
            data = response.json()
            users_data = data.get("users", []) 
            for user_data in users_data:
                user = User(
                    name=f"{user_data['firstName']} {user_data['lastName']}",
                    email=user_data['email'],
                    mobile=user_data['phone'],
                    username=user_data['username']
                )
                self.db.add(user)
            
            self.db.commit()
            return users_data

    def get_user(self, user_id: uuid.UUID):
        try: 
            return self.db.query(User).filter_by(id=user_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting user with id {user_id}: {e}")
            return None


    def get_all_users(self):
        try:
            return self.db.query(User).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting users: {e}")
            return None

    def create_user(self, user: UserCreate):
        existing_user_email = self.db.query(User).filter(
            (User.email == user.email) 
        ).first() 
        existing_user_username = self.db.query(User).filter(
            (User.username == user.username)).first() 
        

        if existing_user_email or existing_user_username:
            logger.error(f"Either User with email {user.email}, or username {user.username}, already exists")
            return None

        db_user = User(
            name=user.name,
            email=user.email,
            mobile=user.mobile,
            username=user.username,
        )
        try:
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            logger.info(f"User created with id {db_user.id}")
            return db_user
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error creating user: {e}")
            return None

    def update_user(self, user_id: uuid.UUID, user: UserUpdate):
        db_user = self.get_user(user_id)
        if not db_user:
            logger.error(f"User with id {user_id} not found for update")
            return None
        try:
            for key, value in user.dict(exclude_unset=True).items():
                setattr(db_user, key, value)
            self.db.commit()
            self.db.refresh(db_user)
            logger.info(f"User with id {user_id} updated")
            return db_user
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating user with id {user_id}: {e}")
            return None

    def delete_user(self, user_id: uuid.UUID):
        db_user = self.get_user(user_id)
        if not db_user:
            logger.error(f"User with id {user_id} not found for deletion")
            return None
        try:
            self.db.delete(db_user)
            self.db.commit()
            logger.info(f"User with id {user_id} deleted")
            return db_user
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting user with id {user_id}: {e}")
            return None
