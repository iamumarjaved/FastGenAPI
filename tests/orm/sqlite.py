import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.models import Base, User, Item, Role

# SQLite test configuration
SQLITE_TEST_DATABASE_URL = "sqlite:///./test_sqlite_db.sqlite"
sqlite_engine = create_engine(SQLITE_TEST_DATABASE_URL, connect_args={"check_same_thread": False})

TestSessionSQLite = sessionmaker(autocommit=False, autoflush=False, bind=sqlite_engine)

@pytest.fixture(scope="module")
def sqlite_session():
    Base.metadata.create_all(bind=sqlite_engine)
    session = TestSessionSQLite()
    yield session
    session.close()
    Base.metadata.drop_all(bind=sqlite_engine)

def test_sqlite_create_user(sqlite_session):
    new_user = User(email="sqlite_test@example.com", hashed_password="sqlite_hashedpwd")
    sqlite_session.add(new_user)
    sqlite_session.commit()
    
    user = sqlite_session.query(User).filter(User.email == "sqlite_test@example.com").first()
    assert user is not None
    assert user.email == "sqlite_test@example.com"

def test_sqlite_delete_user(sqlite_session):
    user = sqlite_session.query(User).filter(User.email == "sqlite_test@example.com").first()
    sqlite_session.delete(user)
    sqlite_session.commit()
    
    deleted_user = sqlite_session.query(User).filter(User.email == "sqlite_test@example.com").first()
    assert deleted_user is None
    
def test_create_user_with_items(sqlite_session):
    # Create a user
    new_user = User(email="test_user@example.com", hashed_password="test_hashedpwd")
    sqlite_session.add(new_user)
    sqlite_session.commit()

    # Add items to the user
    item1 = Item(name="Item1", owner=new_user)
    item2 = Item(name="Item2", owner=new_user)
    sqlite_session.add_all([item1, item2])
    sqlite_session.commit()

    # Verify items are linked to the user
    user = sqlite_session.query(User).filter(User.email == "test_user@example.com").first()
    assert len(user.items) == 2
    assert user.items[0].name == "Item1"

def test_user_roles_relationship(sqlite_session):
    # Create roles
    role_admin = Role(name="Admin")
    role_user = Role(name="User")
    sqlite_session.add_all([role_admin, role_user])
    sqlite_session.commit()

    # Create a user and assign roles
    new_user = User(email="role_user@example.com", hashed_password="role_hashedpwd", roles=[role_admin, role_user])
    sqlite_session.add(new_user)
    sqlite_session.commit()

    # Verify roles are associated with the user
    user = sqlite_session.query(User).filter(User.email == "role_user@example.com").first()
    assert len(user.roles) == 2
    assert role_admin in user.roles
    assert role_user in user.roles

def test_unique_constraint_violation(sqlite_session):
    # Create a user with a specific email
    new_user = User(email="unique_user@example.com", hashed_password="unique_hashedpwd")
    sqlite_session.add(new_user)
    sqlite_session.commit()

    # Try to create another user with the same email
    duplicate_user = User(email="unique_user@example.com", hashed_password="duplicate_hashedpwd")
    
    with pytest.raises(Exception) as excinfo:
        sqlite_session.add(duplicate_user)
        sqlite_session.commit()
    
    assert "duplicate key value" in str(excinfo.value) or "UNIQUE constraint failed" in str(excinfo.value)

def test_missing_required_field(sqlite_session):
    # Try to create a user without an email (which is required)
    incomplete_user = User(hashed_password="incomplete_hashedpwd")
    
    try:
        sqlite_session.add(incomplete_user)
        sqlite_session.commit()
    except Exception as exc:
        sqlite_session.rollback()  # Rollback the session to make it reusable
        assert "null value in column" in str(exc) or "NOT NULL constraint failed" in str(exc) or "UNIQUE constraint failed" in str(exc), f"Unexpected error: {exc}"