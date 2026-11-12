from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import SignupRequest, LoginRequest
from app.core.security import hash_password, verify_password

class UserAlreadyExists(Exception):
    pass

def register_user(
        db: Session,
        signup: SignupRequest
) -> User :
    #check if email exists
    existing_user = db.scalar( select(User).where( User.email == str(signup.email)))

    if existing_user:
        raise UserAlreadyExists

    
    hashed_pw = hash_password(signup.password)
    user = User(email=str(signup.email), password_hash=hashed_pw)
    db.add(user)

    try:
        db.commit()
        db.refresh(user)

    except IntegrityError:
        db.rollback()

        raise UserAlreadyExists

    return user


def login_user(
        db: Session,
        login: LoginRequest) -> User|None:
    email = login.email
    password = login.password

    user = db.scalar(select(User).where(
        User.email == email
    ))

    if user is None:
        return None

    if not verify_password(password, user.password_hash):
        return None
    
    if not user.is_active:
        return None
    
    return user

        

    



    