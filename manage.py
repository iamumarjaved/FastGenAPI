import typer
import subprocess
from pathlib import Path
from src.setup import setup_plantuml
from src.mermaid import install_mermaid_cli
import platform
import subprocess
import os

app = typer.Typer()

def check_admin():
    """Check if the script is running with administrative privileges."""
    try:
        is_admin = os.system("net session >nul 2>&1")
        if is_admin != 0:
            typer.secho("This script requires administrative privileges. Please run as an administrator.", fg="red")
            raise PermissionError("Administrator privileges required.")
    except PermissionError as e:
        raise e

def check_graphviz_installed():
    """Check if Graphviz is installed on the system."""
    try:
        subprocess.run(["dot", "-V"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False

def refresh_system_path():
    """Refresh system PATH to ensure Chocolatey is immediately available."""
    choco_path = r'C:\ProgramData\chocolatey\bin'
    if choco_path not in os.environ["PATH"]:
        os.environ["PATH"] += os.pathsep + choco_path
        typer.echo(f"Chocolatey path added: {choco_path}")
        
    print(choco_path in os.environ["PATH"])

def install_chocolatey():
    """Install Chocolatey if not already installed."""
    try:
        subprocess.run(["choco", "-v"], check=True)
        typer.echo("Chocolatey is already installed.")
    except FileNotFoundError:
        typer.echo("Chocolatey is not installed. Installing Chocolatey...")
        command = (
            'Set-ExecutionPolicy Bypass -Scope Process -Force; '
            '[System.Net.ServicePointManager]::SecurityProtocol = '
            '[System.Net.ServicePointManager]::SecurityProtocol -bor 3072; '
            'iex ((New-Object System.Net.WebClient).DownloadString("https://community.chocolatey.org/install.ps1"))'
        )
        try:
            subprocess.run(["powershell", "-Command", command], check=True)
            refresh_system_path()  # Refresh the system PATH
            typer.echo("Chocolatey installed successfully.")
        except subprocess.CalledProcessError as e:
            typer.secho(f"Error during Chocolatey installation: {e}", fg="red")
            raise

def install_graphviz():
    """Install Graphviz based on the operating system."""
    current_os = platform.system()
    
    if current_os == "Windows":
        typer.echo("Detected Windows OS. Checking for Chocolatey...")
        try:
            install_chocolatey()  # Ensure Chocolatey is installed
            typer.echo("Chocolatey is installed. Installing Graphviz...")
            subprocess.run(["choco", "install", "graphviz", "-y"], check=True)
            typer.secho("Graphviz installed successfully.", fg="green")
        except subprocess.CalledProcessError as e:
            typer.secho(f"Error during Graphviz installation: {str(e)}", fg="red")
    elif current_os == "Linux":
        typer.echo("Detected Linux OS. Installing Graphviz using apt...")
        try:
            subprocess.run(["sudo", "apt-get", "install", "-y", "graphviz"], check=True)
            typer.secho("Graphviz installed successfully.", fg="green")
        except subprocess.CalledProcessError as e:
            typer.secho(f"Error during Graphviz installation on Linux: {str(e)}", fg="red")
    elif current_os == "Darwin":
        typer.echo("Detected macOS. Installing Graphviz via Homebrew...")
        try:
            subprocess.run(["brew", "install", "graphviz"], check=True)
            typer.secho("Graphviz installed successfully.", fg="green")
        except subprocess.CalledProcessError as e:
            typer.secho(f"Error during Graphviz installation on macOS: {e}", fg="red")
    else:
        typer.secho(f"Unsupported OS: {current_os}. Please install Graphviz manually.", fg="red")



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
    install_graphviz()  
    result = subprocess.run(["eralchemy", "render", "src.models", "schema_erd.pdf"], capture_output=True)
    if result.returncode == 0:
        typer.echo("ERD diagram generated as schema_erd.pdf")
    else:
        typer.echo(f"Error: {result.stderr.decode()}")


@app.command()
def generate_erd():
    """Generate an Entity Relationship Diagram (ERD)"""
    typer.echo("Generating ERD from the database schema...")
    setup_plantuml()  
    install_graphviz()  
    result = subprocess.run(["eralchemy", "-i", "postgresql+psycopg2://username:password@localhost/dbname", "-o", "erd_from_db.pdf"], capture_output=True)
    if result.returncode == 0:
        typer.echo("ERD generated as erd_from_db.pdf")
    else:
        typer.echo(f"Error: {result.stderr.decode()}")


@app.command()
def generate_class_diagram():
    """Generate Class Diagram using PlantUML"""
    setup_plantuml()  
    typer.echo("Generating Class Diagram using PlantUML...")
    result = subprocess.run(["java", "-jar", "plantuml.jar", "class_diagram.puml"], capture_output=True)
    if result.returncode == 0:
        typer.echo("Class Diagram generated as class_diagram.png")
    else:
        typer.echo(f"Error: {result.stderr.decode()}")


@app.command()
def generate_mermaid_diagram():
    """Generate diagrams using Mermaid.js"""
    install_mermaid_cli()
    typer.echo("Generating diagram using Mermaid.js...")
    result = subprocess.run(["mmdc", "-i", "diagram.mmd", "-o", "diagram.png"], capture_output=True)
    if result.returncode == 0:
        typer.echo("Diagram generated as diagram.png")
    else:
        typer.echo(f"Error: {result.stderr.decode()}")


if __name__ == "__main__":
    app()
