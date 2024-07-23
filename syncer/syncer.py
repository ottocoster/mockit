import os, os.path
import re
from git import Repo

# Function to normalize CLI command names by removing trailing numbers and underscores
def convert_cli_command(cli_command):
    word_list = cli_command.split('_')
    last_word = word_list[-1]
    all_but_last = '_'.join(word_list[:-1])

    if last_word.isdigit():
        if int(last_word) > 100:
            result = all_but_last + "_" + last_word
        else:
            result = all_but_last
    else:
        normalized_last = re.sub(r'\d+$', '', last_word)
        result = all_but_last + "_" + normalized_last
    
    result = result.replace("_", "")
    return result

def safe_open_w(path):
    ''' Open "path" for writing, creating any parent directories as needed.
    '''
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return open(path, 'w')


# Function to extract the numeric part from the filename
def extract_number(filename, template_name):
    sub_filename = filename.replace(template_name, "")
    match = re.search(r'_(\d+)', sub_filename)
    return int(match.group(1)) if match else -1

# Function to scrape data from repo
def scrape_templates_from_repo(repo_path, config_dir):
    # Walk through the /tests directory to find .raw files
    tests_path = os.path.join(repo_path, 'tests')

    for root, dirs, files in os.walk(tests_path):
        cli_path = os.path.relpath(root, tests_path)
        path_list = cli_path.split(os.sep)
        if len(path_list) != 2:
            continue

        # Vendor folder
        vendor = path_list[0]

        # CLI file
        cli_command = path_list[1]
        formatted_cli_command = cli_command.replace("_", " ")

        # Only get the cli content files
        filtered_files = [file for file in files if file.endswith('.raw')]
        
        # Sort the files based on the extracted numeric part
        sorted_files = sorted(filtered_files, key=lambda x: extract_number(x, cli_command), reverse=True)
        if not sorted_files:
            continue
        
        file = sorted_files[0]

        # File found
        print("file:", file)
        print("folder:", root)
        
        raw_file_path = os.path.join(root, file)
        with open(raw_file_path, 'r') as raw_file:
            cli_content = raw_file.read()

        # Save file in the config folder configs/<vendor>/templates/<cli_command>.text
        save_path = os.path.join(config_dir, vendor, "templates", formatted_cli_command + ".txt")
        with safe_open_w(save_path) as save_file:
            save_file.write(cli_content)

# Function to clone or pull the repository
def clone_or_pull_repo(repo_url, repo_path):
    if os.path.exists(repo_path):
        repo = Repo(repo_path)
        repo.remotes.origin.pull()
    else:
        Repo.clone_from(repo_url, repo_path)

# Main function
def main():
    repo_url = 'https://github.com/networktocode/ntc-templates'
    repo_path = './ntc-templates'
    config_dir = '../configs'
    
    # Clone or pull the repository
    clone_or_pull_repo(repo_url, repo_path)
    
    # Store the files
    scrape_templates_from_repo(repo_path, config_dir)

if __name__ == '__main__':
    main()
