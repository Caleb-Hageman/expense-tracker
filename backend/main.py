import fastapi as _fastapi
from typing import TYPE_CHECKING, List
import sqlalchemy.orm as _orm
from backend import schemas as _schemas
from backend import models as _models
from backend import services as _services
from backend import database as _db
from backend import auth as _auth
from fastapi.security import OAuth2PasswordRequestForm

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

app = _fastapi.FastAPI()

######### User API endpoints
@app.post("/api/signup", response_model=_schemas.UserBase)
async def create_user(
    user: _schemas.UserCreate, 
    db: _orm.Session = _fastapi.Depends(_db.get_db)
    ):
    return await _services.create_user(user=user, db=db)

@app.post("/api/login", response_model=_schemas.TokenResponse)
def login_user(form_data: OAuth2PasswordRequestForm = _fastapi.Depends(), db: _orm.Session = _fastapi.Depends(_db.get_db),):
    db_user = _services.verify_user(
        user_data=_schemas.UserLogin(email=form_data.username, password=form_data.password),
        db=db
    )

    access_token = _auth.create_access_token(db_user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

#
# @app.delete("/api/remove-user")
# async def delete_user(current_user: _models.User = _fastapi.Depends(_auth.get_current_user), db: _orm.Session = _fastapi.Depends(_db.get_db)):
#     await _services.delete_user(current_user.id, db)

######## Category API endpoints
@app.post("/api/new-category", response_model=_schemas.CategoryResponse)
async def create_category(
    cat: _schemas.CategoryCreate,
    current_user: _models.User = _fastapi.Depends(_auth.get_current_user),
    db: _orm.Session = _fastapi.Depends(_db.get_db)
    ):
    return await _services.create_category(cat=cat, usr_id=current_user.id, db=db)