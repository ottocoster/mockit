import os

# Define the source folder and file
source_folder = "a10"
source_file = os.path.join(source_folder, "a10_server.py")

# Get the list of all folders in the current directory
all_folders = [f for f in os.listdir() if os.path.isdir(f) and f != source_folder]

# Read the content of the source file
with open(source_file, 'r') as file:
    content = file.read()

# Function to replace and save the file
def replace_and_copy(folder, content):
    new_content = content.replace("a10", folder)
    target_file = os.path.join(folder, f"{folder}_server.py")
    with open(target_file, 'w') as file:
        file.write(new_content)

# Iterate over all folders and copy the modified content
for folder in all_folders:
    replace_and_copy(folder, content)

print("Files copied and modified successfully.")
