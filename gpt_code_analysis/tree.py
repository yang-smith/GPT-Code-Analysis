import os

def save_structure_to_file(directory_path, output_file_path, ignore_file_path):
    ignore_list = []
    with open(ignore_file_path, 'r') as ignore_file:
        ignore_list = [os.path.normpath(line.strip()).replace("\\", "/") for line in ignore_file]

    with open(output_file_path, 'w') as file:
        for dirpath, dirnames, filenames in os.walk(directory_path):
            relative_dirpath = os.path.relpath(dirpath, directory_path)
            # 检查当前文件夹是否在忽略列表中，或者是否以'.'开头
            if relative_dirpath in ignore_list or os.path.basename(dirpath).startswith('.'):
                dirnames[:] = []  # 清空子目录列表，这样我们就不会进入这个目录了
                continue
            file.write(f'{relative_dirpath}\n')
            for filename in filenames:
                # 检查当前文件是否在忽略列表中，或者是否以'.'开头
                if os.path.join(relative_dirpath, filename) in ignore_list or filename.startswith('.'):
                    continue
                file.write(f'\t{filename}\n')

# 使用方法
# save_structure_to_file('./test', './test/test_output.txt', './test/ignore.txt')
