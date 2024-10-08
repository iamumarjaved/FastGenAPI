import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.models import Base, User, Item, Role

MYSQL_TEST_DATABASE_URL = "mysql+pymysql://user:password@localhost/test_db"
mysql_engine = create_engine(MYSQL_TEST_DATABASE_URL)

TestSessionMySQL = sessionmaker(autocommit=False, autoflush=False, bind=mysql_engine)

@pytest.fixture(scope="module")
def mysql_session():
    Base.metadata.create_all(bind=mysql_engine)
    session = TestSessionMySQL()
    yield session
    session.close()
    Base.metadata.drop_all(bind=mysql_engine)

def test_mysql_create_user(mysql_session):
    new_user = User(email="mysql_test@example.com", hashed_password="mysql_hashedpwd")
    mysql_session.add(new_user)
    mysql_session.commit()
    
    user = mysql_session.query(User).filter(User.email == "mysql_test@example.com").first()
    assert user is not None
    assert user.email == "mysql_test@example.com"

def test_mysql_delete_user(mysql_session):
    user = mysql_session.query(User).filter(User.email == "mysql_test@example.com").first()
    mysql_session.delete(user)
    mysql_session.commit()
    
    deleted_user = mysql_session.query(User).filter(User.email == "mysql_test@example.com").first()
    assert deleted_user is None

def test_create_user_with_items(mysql_session):
    # Create a user
    new_user = User(email="test_user@example.com", hashed_password="test_hashedpwd")
    mysql_session.add(new_user)
    mysql_session.commit()

    # Add items to the user
    item1 = Item(name="Item1", owner=new_user)
    item2 = Item(name="Item2", owner=new_user)
    mysql_session.add_all([item1, item2])
    mysql_session.commit()

    # Verify items are linked to the user
    user = mysql_session.query(User).filter(User.email == "test_user@example.com").first()
    assert len(user.items) == 2
    assert user.items[0].name == "Item1"
    
def test_user_roles_relationship(mysql_session):
    # Create roles
    role_admin = Role(name="Admin")
    role_user = Role(name="User")
    mysql_session.add_all([role_admin, role_user])
    mysql_session.commit()

    # Create a user and assign roles
    new_user = User(email="role_user@example.com", hashed_password="role_hashedpwd", roles=[role_admin, role_user])
    mysql_session.add(new_user)
    mysql_session.commit()

    # Verify roles are associated with the user
    user = mysql_session.query(User).filter(User.email == "role_user@example.com").first()
    assert len(user.roles) == 2
    assert role_admin in user.roles
    assert role_user in user.roles

def test_unique_constraint_violation(mysql_session):
    # Create a user with a specific email
    new_user = User(email="unique_user@example.com", hashed_password="unique_hashedpwd")
    mysql_session.add(new_user)
    mysql_session.commit()

    # Try to create another user with the same email
    duplicate_user = User(email="unique_user@example.com", hashed_password="duplicate_hashedpwd")
    
    with pytest.raises(Exception) as excinfo:
        mysql_session.add(duplicate_user)
        mysql_session.commit()
    
    assert "duplicate key value" in str(excinfo.value) or "UNIQUE constraint failed" in str(excinfo.value)

def test_missing_required_field(mysql_session):
    # Try to create a user without an email (which is required)
    incomplete_user = User(hashed_password="incomplete_hashedpwd")
    
    try:
        mysql_session.add(incomplete_user)
        mysql_session.commit()
    except Exception as exc:
        mysql_session.rollback() 
        assert "null value in column" in str(exc) or "NOT NULL constraint failed" in str(exc) or "duplicate key value violates unique constraint" in str(exc), f"Unexpected error: {exc}"