from typing import TYPE_CHECKING
from backend import database as _db
from backend import models as _models
from backend import schemas as _schemas
from backend import auth as _auth
from fastapi import HTTPException, status

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

def _add_tables():
    return _db.Base.metadata.create_all(bind=_db.engine)

# ============================================================================
# User Services
# ============================================================================

async def create_user(user: _schemas.UserCreate, db: "Session") -> _schemas.UserBase:
    db_user = _models.User(email=user.email, hashed_password=_auth.hash_password(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return _schemas.UserResponse.model_validate(db_user)

def verify_user(user_data: _schemas.UserLogin, db: "Session") -> _models.User:
    user = db.query(_models.User).filter(_models.User.email == user_data.email).first()
    
    if not user or not _auth.verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return user

# async def delete_user(user_id: int, db):
#     user = db.query(_models.User).filter(_models.User.id == user_id).first()

#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found",
#         )

#     db.delete(user)
#     db.commit()

# ============================================================================
# Category Services
# ============================================================================
async def create_category(cat: _schemas.CategoryCreate, usr_id: int, db: "Session") -> _schemas.CategoryBase:
    new_cat = _models.Category(
        user_id=usr_id, 
        name=cat.name, 
        type=cat.type, 
        color=cat.color, 
        icon=cat.icon
    )

    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)

    return _schemas.CategoryResponse.model_validate(new_cat)
# ============================================================================
# Transaction Services
# ============================================================================

# ============================================================================
# Budget Schemas
# ============================================================================

# ============================================================================
# Recurring Transaction Schemas
# ============================================================================