import subprocess

def install_mermaid_cli():
    try:
        subprocess.run(["npm", "-v"], check=True)
        subprocess.run(["npm", "install", "-g", "@mermaid-js/mermaid-cli"], check=True)
        print("Mermaid CLI installed successfully.")
    except subprocess.CalledProcessError:
        raise EnvironmentError("npm is not installed. Please install Node.js and npm.")

install_mermaid_cli()
