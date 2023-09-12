import re


def parse_chat(chat):
    # Get all blocks enclosed by #### and extract the file path and the content following it
    regex = r"####\s*(.*?)\s*####\n?(.+?)(?=####|$)"
    matches = re.finditer(regex, chat, re.DOTALL)

    files = []
    for match in matches:
        # Get the file path
        path = match.group(1)

        # Strip the filename of any non-allowed characters and convert / to \
        path = re.sub(r'[\:<>"|?*]', "", path)

        # Get the code/content
        code = match.group(2).strip()  # strip is added to remove unwanted leading/trailing spaces

        # Add the file to the list
        files.append((path, code))

    # Return the files
    return files


def to_files(chat, workspace):
    workspace["all_output.txt"] = chat

    files = parse_chat(chat)
    for file_name, file_content in files:
        workspace[file_name] = file_content
