import os

# Define the base directory
base_dir = "new"

# Define the directory structure
structure = {
    "templates": ["base.html", "home.html", "login.html", "register.html"],
    "static": {
        "css": ["styles.css"],
        "js": ["scripts.js"],
        "images": [],
    },
    "logs": [],
    "uploads": [],
    "config": ["__init__.py", "config.py"],
    "blueprints": {
        "auth": ["__init__.py", "routes.py", "forms.py"],
        "song_contest": ["__init__.py", "routes.py", "forms.py", "models.py"],
    },
}

# Function to create directories and files
def create_structure(base, structure):
    for key, value in structure.items():
        dir_path = os.path.join(base, key)
        os.makedirs(dir_path, exist_ok=True)
        if isinstance(value, list):  # If the value is a list, create files
            for file in value:
                file_path = os.path.join(dir_path, file)
                if not os.path.exists(file_path):
                    with open(file_path, "w") as f:
                        f.write(f"# {file} placeholder\n")
        elif isinstance(value, dict):  # If the value is a dict, recurse
            create_structure(dir_path, value)

# Create the base structure
os.makedirs(base_dir, exist_ok=True)
create_structure(base_dir, structure)

print(f"Project structure created under {base_dir}")
