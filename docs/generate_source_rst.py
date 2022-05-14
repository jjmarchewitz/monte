# TODO: Extract all of the TODO: markers in the reptory and put them into TODO.md,
# sorted if pible

from os import getcwd, listdir, makedirs, path, sep
from re import findall


SUPER_PACKAGE_NAME = "algo_pg"
SUPER_RST_DIR = "source_test"


def find_python_source_files_in_dir(search_directory):
    list_of_py_src_files = []
    items_in_dir = listdir(search_directory)

    files_in_dir = [f for f in items_in_dir if path.isfile(
        path.join(search_directory, f))]
    subdirs_in_dir = [f for f in items_in_dir if path.isdir(
        path.join(search_directory, f))]

    for f in files_in_dir:
        full_file_path = path.join(search_directory, f)
        root, ext = path.splitext(full_file_path)

        if ext == ".py":
            list_of_py_src_files.append(full_file_path)

    for subdir in subdirs_in_dir:
        full_subdir_path = path.join(search_directory, subdir)
        list_of_py_src_files.extend(find_python_source_files_in_dir(full_subdir_path))

    return list_of_py_src_files


def create_rst_for_src_file(base_dir, relative_src_file_path):

    full_rst_file_path = path.join(
        base_dir, relative_src_file_path).replace(
        ".py", ".rst")

    folder_path, filename = path.split(full_rst_file_path)

    module_name = filename.split(".")[0]

    import_name = relative_src_file_path.lstrip(
        SUPER_PACKAGE_NAME + sep).rstrip(".py").replace(sep, ".")

    if not path.exists(folder_path):
        makedirs(folder_path)

    with open(full_rst_file_path, "w") as f:

        equals_sign_barrier_line = ""
        for _ in module_name:
            equals_sign_barrier_line += "="

        file_text = f"{module_name}\n{equals_sign_barrier_line}\n\n.. automodule:: "
        file_text += f"{import_name}\n\t:members:\n\n.. toctree::\n\t:maxdepth: 4"

        f.write(file_text)


def create_package_rst_files(base_dir):
    pass


def main():
    repo_dir = findall("^.*algo-playground", getcwd())[0]
    src_dir = f"{repo_dir}{sep}src"
    rst_dir = path.join(repo_dir, "docs", SUPER_RST_DIR)

    py_src_files_list = find_python_source_files_in_dir(src_dir)

    relative_src_file_path_list = [
        src_file_path.split("src/")[1] for src_file_path in py_src_files_list]

    for relative_src_file_path in relative_src_file_path_list:
        create_rst_for_src_file(rst_dir, relative_src_file_path)

    create_package_rst_files(rst_dir)


if __name__ == "__main__":
    main()
