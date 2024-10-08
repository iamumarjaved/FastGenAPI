import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.models import Base, User, Item, Role

POSTGRES_TEST_DATABASE_URL = "postgresql://root:1210@localhost:5433/FastGenAPI"
postgres_engine = create_engine(POSTGRES_TEST_DATABASE_URL)

TestSessionPostgres = sessionmaker(autocommit=False, autoflush=False, bind=postgres_engine)

@pytest.fixture(scope="module")
def postgres_session():
    Base.metadata.create_all(bind=postgres_engine)
    session = TestSessionPostgres()
    yield session
    session.close()
    Base.metadata.drop_all(bind=postgres_engine)

def test_postgres_create_user(postgres_session):
    new_user = User(email="postgres_test@example.com", hashed_password="postgres_hashedpwd")
    postgres_session.add(new_user)
    postgres_session.commit()
    
    user = postgres_session.query(User).filter(User.email == "postgres_test@example.com").first()
    assert user is not None
    assert user.email == "postgres_test@example.com"

def test_postgres_update_user(postgres_session):
    user = postgres_session.query(User).filter(User.email == "postgres_test@example.com").first()
    user.email = "updated_postgres@example.com"
    postgres_session.commit()
    
    updated_user = postgres_session.query(User).filter(User.email == "updated_postgres@example.com").first()
    assert updated_user is not None

def test_create_user_with_items(postgres_session):
    # Create a user
    new_user = User(email="test_user@example.com", hashed_password="test_hashedpwd")
    postgres_session.add(new_user)
    postgres_session.commit()

    # Add items to the user
    item1 = Item(name="Item1", owner=new_user)
    item2 = Item(name="Item2", owner=new_user)
    postgres_session.add_all([item1, item2])
    postgres_session.commit()

    # Verify items are linked to the user
    user = postgres_session.query(User).filter(User.email == "test_user@example.com").first()
    assert len(user.items) == 2
    assert user.items[0].name == "Item1"
    
def test_user_roles_relationship(postgres_session):
    # Create roles
    role_admin = Role(name="Admin")
    role_user = Role(name="User")
    postgres_session.add_all([role_admin, role_user])
    postgres_session.commit()

    # Create a user and assign roles
    new_user = User(email="role_user@example.com", hashed_password="role_hashedpwd", roles=[role_admin, role_user])
    postgres_session.add(new_user)
    postgres_session.commit()

    # Verify roles are associated with the user
    user = postgres_session.query(User).filter(User.email == "role_user@example.com").first()
    assert len(user.roles) == 2
    assert role_admin in user.roles
    assert role_user in user.roles

def test_unique_constraint_violation(postgres_session):
    # Create a user with a specific email
    new_user = User(email="unique_user@example.com", hashed_password="unique_hashedpwd")
    postgres_session.add(new_user)
    postgres_session.commit()

    # Try to create another user with the same email
    duplicate_user = User(email="unique_user@example.com", hashed_password="duplicate_hashedpwd")
    
    with pytest.raises(Exception) as excinfo:
        postgres_session.add(duplicate_user)
        postgres_session.commit()
    
    assert "duplicate key value" in str(excinfo.value) or "UNIQUE constraint failed" in str(excinfo.value)

def test_missing_required_field(postgres_session):
    # Try to create a user without an email (which is required)
    incomplete_user = User(hashed_password="incomplete_hashedpwd")
    
    try:
        postgres_session.add(incomplete_user)
        postgres_session.commit()
    except Exception as exc:
        postgres_session.rollback() 
        assert "null value in column" in str(exc) or "NOT NULL constraint failed" in str(exc) or "duplicate key value violates unique constraint" in str(exc), f"Unexpected error: {exc}"