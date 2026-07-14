import os

# Directories to ignore
IGNORE_DIRS = [
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "build",
    "dist"
]


def traverse_directory(root_directory):
    for current_path, directories, files in os.walk(root_directory):

        # Remove ignored directories
        directories[:] = [
            directory
            for directory in directories
            if directory not in IGNORE_DIRS
        ]

        print(f"\n📁 Directory: {current_path}")

        for file in files:
            file_name, extension = os.path.splitext(file)

            print(f"   📄 {file}")
            print(f"      Extension: {extension if extension else 'No Extension'}")


# Starting directory
root_directory = "."

traverse_directory(root_directory)