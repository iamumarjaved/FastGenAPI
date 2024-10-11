import typer
import subprocess
from pathlib import Path
from src.setup import setup_plantuml
from src.mermaid import install_mermaid_cli


app = typer.Typer()


@app.command()
def runserver():
    """Run the FastAPI server using Uvicorn"""
    typer.echo("Starting the server...")
    subprocess.run(["uvicorn", "src.main:app", "--reload"])


@app.command()
def create_endpoint(name: str):
    """Generate a new FastAPI endpoint"""
    dir_path = Path("src/api/v1/endpoints/")
    dir_path.mkdir(parents=True, exist_ok=True)

    file_path = dir_path / f"{name}.py"
    file_content = f"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_{name}():
    return {{"message": "{name} endpoint working"}}
    """
    file_path.write_text(file_content)
    typer.echo(f"Endpoint {name} created at {file_path}.")


@app.command()
def create_model(name: str):
    """Generate a new SQLAlchemy model"""
    dir_path = Path("src/models/")
    dir_path.mkdir(parents=True, exist_ok=True) 

    file_path = dir_path / f"{name}.py"
    file_content = f"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class {name}(Base):
    __tablename__ = '{name.lower()}'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    """
    file_path.write_text(file_content)
    typer.echo(f"Model {name} created at {file_path}.")


@app.command()
def makemigrations():
    """Create new migrations and apply to the database"""
    typer.echo("Creating migrations...")
    subprocess.run(["alembic", "revision", "--autogenerate", "-m", "New Migration"])
    typer.echo("Applying migrations...")
    subprocess.run(["alembic", "upgrade", "head"])
    typer.echo("Migrations applied.")


@app.command()
def auto_generate_erd():
    """Generate ERD from SQLAlchemy models"""
    typer.echo("Generating ERD diagram from models...")
    subprocess.run(["eralchemy", "--model", "src.models", "--output", "schema_erd.pdf"])
    typer.echo("ERD diagram generated as schema_erd.pdf")


@app.command()
def generate_erd():
    """Generate an Entity Relationship Diagram (ERD)"""
    typer.echo("Generating ERD from the database schema...")
    setup_plantuml()  
    subprocess.run(["eralchemy", "-i", "postgresql+psycopg2://username:password@localhost/dbname", "-o", "erd_from_db.pdf"])
    typer.echo("ERD generated as erd_from_db.pdf.")


@app.command()
def generate_class_diagram():
    """Generate Class Diagram using PlantUML"""
    setup_plantuml()  
    typer.echo("Generating Class Diagram using PlantUML...")
    subprocess.run(["java", "-jar", "plantuml.jar", "class_diagram.puml"])
    typer.echo("Class Diagram generated as class_diagram.png.")

@app.command()
def generate_mermaid_diagram():
    """Generate diagrams using Mermaid.js"""
    install_mermaid_cli()  
    typer.echo("Generating diagram using Mermaid.js...")
    subprocess.run(["mmdc", "-i", "diagram.mmd", "-o", "diagram.png"])
    typer.echo("Diagram generated as diagram.png.")


if __name__ == "__main__":
    app()
