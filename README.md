
# FashGenAPI

**FashGenAPI** is a versatile package designed to simplify and accelerate your FastAPI project development. It provides essential tools for automatic generation of project structure, models, endpoints, documentation, diagrams, and database management, all integrated into a single command-line interface (CLI).

## Features

### 1. Auto-Generated Documentation
- **Swagger & ReDoc**: Automatically integrates Swagger UI and ReDoc for easy API documentation.
- **Custom Templates**: Customize the look and feel of your API documentation with predefined templates.
- **Real-time updates**: Auto-generates documentation when project components are modified.

### 2. Authentication and Authorization
- **JWT-based Authentication**: Built-in support for JWT (JSON Web Token) to secure your API.
- **OAuth2**: Easily integrate OAuth2 for external authentication providers.
- **Role-based Access Control (RBAC)**: Predefined user roles and permissions for easy management of access levels.

### 3. Database Migrations and ORM Integration
- **SQLAlchemy**: Integrated SQLAlchemy ORM for smooth database interaction.
- **Alembic Migrations**: Auto-generate database migration scripts.
- **Multiple Database Support**: Configure PostgreSQL, SQLite, or other databases with ease.

### 4. Auto-Generate ERD (Entity-Relationship Diagrams)
- Automatically generate ERD diagrams from SQLAlchemy models or directly from your database schema using ERAlchemy.
  
### 5. Class Diagram Generation (UML)
- Automatically generate class diagrams using PlantUML.

### 6. Mermaid.js Diagram Generation
- Generate flowcharts and other diagrams using Mermaid.js via CLI.

### 7. API Endpoint and Model Generation
- **Custom Endpoints**: Automatically generate new FastAPI endpoints with a simple command.
- **SQLAlchemy Models**: Generate basic SQLAlchemy models with one command.

---

## Installation

1. Install the package using pip:
    ```bash
    pip install fastapi-boilerplate-generator
    ```

2. Install the dependencies from `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

---

## CLI Usage

### Run the FastAPI Server
```bash
python manage.py runserver
```

### Create a New Endpoint
```bash
python manage.py create-endpoint <endpoint_name>
```
- Example:
    ```bash
    python manage.py create-endpoint users
    ```

### Create a New SQLAlchemy Model
```bash
python manage.py create-model <model_name>
```
- Example:
    ```bash
    python manage.py create-model User
    ```

### Database Migrations
```bash
python manage.py makemigrations
```

### Generate ERD from SQLAlchemy Models
```bash
python manage.py auto-generate-erd
```

### Generate Class Diagrams
```bash
python manage.py generate-class-diagram
```

### Generate Diagrams using Mermaid.js
```bash
python manage.py generate-mermaid-diagram
```

---

## Examples

### Example of Generated Endpoint (`users.py`)
```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_users():
    return {"message": "Users endpoint working"}
```

### Example of Generated SQLAlchemy Model (`user.py`)
```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
```

---

## Configuration

### Database Configuration
You can configure your database connection inside your FastAPI app:
```python
DATABASE_URL = "postgresql+psycopg2://username:password@localhost/dbname"
```

### JWT Configuration
To secure your API with JWT, define your secret key and expiration inside your configuration file:
```python
JWT_SECRET = "your_jwt_secret"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_TIME_MINUTES = 30
```

---

## Contributing

Contributions are welcome! Please submit a pull request or open an issue if you find any bugs or want to suggest new features.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

![PyPI](https://img.shields.io/pypi/v/FastGenAPI)
![Downloads](https://img.shields.io/pypi/dm/FastGenAPI)
