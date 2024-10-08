from src.models.models import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
def to_pydantic(db_obj, pydantic_model):
    return pydantic_model.from_orm(db_obj)
