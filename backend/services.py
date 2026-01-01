import database as _db
import models as _models

def _add_tables():
    return _db.Base.metadata.create_all(bind=_db.engine)