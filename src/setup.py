import os
import subprocess
import requests
from requests.exceptions import ConnectionError, Timeout
import typer

def setup_plantuml():
    plantuml_jar = "plantuml.jar"

    # Step 1: Check if Java is installed
    try:
        typer.echo("Checking Java installation...")
        subprocess.run(["java", "-version"], check=True)
    except FileNotFoundError:
        typer.secho("Java is not installed. Please install Java to use PlantUML.", fg="red")
        return

    # Step 2: Check if PlantUML jar exists, if not download
    if not os.path.exists(plantuml_jar):
        typer.secho("PlantUML jar not found, attempting to download...", fg="yellow")
        try:
            url = "http://sourceforge.net/projects/plantuml/files/plantuml.jar/download"
            response = requests.get(url, stream=True, timeout=30)

            # Check for successful connection
            if response.status_code == 200:
                # Save the file with progress logging
                with open(plantuml_jar, 'wb') as f:
                    total_length = response.headers.get('content-length')
                    if total_length is None:
                        f.write(response.content)
                    else:
                        total_length = int(total_length)
                        for data in response.iter_content(chunk_size=4096):
                            f.write(data)
                            done = int(50 * f.tell() / total_length)
                            typer.echo(f"\r[{'=' * done}{' ' * (50-done)}] {done*2}%", nl=False)
            typer.secho("\nDownloaded plantuml.jar successfully.", fg="green")
        except ConnectionError:
            typer.secho("Failed to connect to the download server. Please check your internet connection.", fg="red")
        except Timeout:
            typer.secho("The download attempt timed out. Please try again later.", fg="red")
        except Exception as e:
            typer.secho(f"An unexpected error occurred: {e}", fg="red")

setup_plantuml()
