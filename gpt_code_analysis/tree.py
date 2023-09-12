import os
import chardet

def get_file_encoding(file_path):
    try:
        with open(file_path, 'rb') as file:
            return chardet.detect(file.read())['encoding']
    except Exception as e:
        print(f"Could not determine the encoding of file {file_path}. Error: {e}")
        return None

def get_ignore_list(directory_path, ignore_file_path):
    ignore_list = []
    
    if not os.path.exists(ignore_file_path):
        print(f"Ignore file path does not exist: {ignore_file_path}")
        return ignore_list

    encoding = get_file_encoding(ignore_file_path)
    if not encoding:
        return ignore_list

    try:
        with open(ignore_file_path, 'r', encoding=encoding) as ignore_file:
            for line in ignore_file:
                full_path = os.path.join(directory_path, line.strip())
                normalized_path = os.path.normpath(full_path).replace("\\", "/")
                ignore_list.append(normalized_path)
    except Exception as e:
        print(f"Error reading ignore file: {e}")

    return ignore_list

def save_structure_to_file(directory_path, output_file_path, ignore_file_path):
    if not os.path.isdir(directory_path):
        print(f"Directory path does not exist: {directory_path}")
        return

    ignore_list = get_ignore_list(directory_path, ignore_file_path)
    
    try:
        with open(output_file_path, 'w', encoding='utf-8') as file:
            for dirpath, dirnames, filenames in os.walk(directory_path):
                normalized_dirpath = os.path.normpath(dirpath).replace("\\", "/")
                if normalized_dirpath in ignore_list or os.path.basename(dirpath).startswith('.'):
                    dirnames[:] = []  # 清空子目录列表，这样我们就不会进入这个目录了
                    continue
                relative_dirpath = os.path.relpath(dirpath, directory_path)
                file.write(f'{relative_dirpath}\n')
                for filename in filenames:
                    full_filepath = os.path.normpath(os.path.join(dirpath, filename)).replace("\\", "/")
                    if full_filepath in ignore_list or filename.startswith('.'):
                        continue
                    file.write(f'\t{filename}\n')
    except Exception as e:
        print(f"Error saving structure to file: {e}")

# 调用方式：
# save_structure_to_file('your_directory_path', 'your_output_file_path', 'your_ignore_file_path')
