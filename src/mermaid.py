import subprocess
import typer

app = typer.Typer()

def check_npm_installed():
    """Check if npm is installed on the system."""
    try:
        subprocess.run(["npm", "-v"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False

def install_mermaid_cli():
    """Install Mermaid CLI using npm."""
    if check_npm_installed():
        try:
            typer.echo("npm is installed, installing Mermaid CLI...")
            subprocess.run(["npm", "install", "-g", "@mermaid-js/mermaid-cli"], check=True)
            typer.secho("Mermaid CLI installed successfully.", fg="green")
        except subprocess.CalledProcessError as e:
            typer.secho(f"Error during installation: {str(e)}", fg="red")
    else:
        typer.secho("npm is not installed. Please install Node.js and npm to use this feature.", fg="red")
        raise EnvironmentError("npm is not installed.")


@app.command()
def setup_mermaid_cli():
    """CLI command to install Mermaid CLI."""
    install_mermaid_cli()

if __name__ == "__main__":
    app()
