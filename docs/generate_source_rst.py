# TODO: Extract all of the TODO: markers in the reptory and put them into TODO.md,
# sorted if pible

from importlib.resources import path
import os
from re import findall, sub


SUPER_PACKAGE_NAME = "algo_pg"
SOURCE_DIR = "source"


def find_python_source_files_in_dir(search_directory):

    list_of_py_src_files = []
    items_in_dir = os.listdir(search_directory)

    files_in_dir = [f for f in items_in_dir if os.path.isfile(
        os.path.join(search_directory, f))]
    subdirs_in_dir = [f for f in items_in_dir if os.path.isdir(
        os.path.join(search_directory, f))]

    for f in files_in_dir:
        full_file_path = os.path.join(search_directory, f)
        root, ext = os.path.splitext(full_file_path)

        if ext == ".py":
            list_of_py_src_files.append(full_file_path)

    for subdir in subdirs_in_dir:
        full_subdir_path = os.path.join(search_directory, subdir)
        list_of_py_src_files.extend(find_python_source_files_in_dir(full_subdir_path))

    return list_of_py_src_files


def create_rst_for_src_file(base_dir, relative_src_file_path):

    full_rst_file_path = os.path.join(
        base_dir, relative_src_file_path).replace(
        ".py", ".rst")

    folder_path, filename = os.path.split(full_rst_file_path)

    module_name = filename.split(".")[0]

    # TODO: VS Code extension pasting into terminal, auto remove the extra line

    import_name = relative_src_file_path.lstrip(SUPER_PACKAGE_NAME).lstrip(
        os.sep).rstrip(".py").replace(os.sep, ".")

    # breakpoint()

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    with open(full_rst_file_path, "w") as f:

        equals_sign_barrier_line = ""
        for _ in module_name:
            equals_sign_barrier_line += "="

        file_text = f"{module_name}\n"
        file_text += f"{equals_sign_barrier_line}\n\n"
        file_text += f".. automodule:: {import_name}\n"
        file_text += f"\t:members:\n\n"
        file_text += f".. toctree::\n"
        file_text += f"\t:maxdepth: 4\n\n"

        f.write(file_text)


def create_package_rst_files(base_dir):

    # TODO: Rename everything to dir instead of package
    for path_being_searched, subpackages, modules_in_package in os.walk(base_dir):
        # parent_package, current_package_name = os.path.split(package_being_searched)

        # breakpoint()

        package_being_searched = os.path.basename(path_being_searched)

        # TODO: Python formatting extension that formats strings into multiple shorter += calls
        with open(f"{path_being_searched}{os.sep}..{os.sep}{package_being_searched}.rst", "w") as f:

            file_text = f"{package_being_searched}\n"

            for _ in package_being_searched:
                file_text += "="

            file_text += "\n\n"
            file_text += ".. toctree::\n"
            file_text += "\t:maxdepth: 4\n\n"

            for subpackage in sorted(subpackages):
                file_text += f"\t{package_being_searched}{os.sep}{subpackage}\n"

            for module in modules_in_package:

                # breakpoint()

                module_matches_subpackage = False

                for subpackage in subpackages:
                    if module == subpackage + ".rst":
                        module_matches_subpackage = True

                if not module_matches_subpackage:
                    file_text += f'\t{package_being_searched}{os.sep}{module.rstrip(".rst")}\n'

            file_text += "\n"

            f.write(file_text)


def main():
    # TODO: Move this information to be global constants
    repo_dir = findall("^.*algo-playground", os.getcwd())[0]
    src_dir = f"{repo_dir}{os.sep}src"
    algo_pg_dir = f"{repo_dir}{os.sep}docs{os.sep}{SOURCE_DIR}{os.sep}{SUPER_PACKAGE_NAME}"
    doc_source_dir = os.path.join(repo_dir, "docs", SOURCE_DIR)

    py_src_files_list = find_python_source_files_in_dir(src_dir)

    relative_src_file_path_list = [
        src_file_path.split("src/")[1] for src_file_path in py_src_files_list]

    # breakpoint()
    for relative_src_file_path in relative_src_file_path_list:
        create_rst_for_src_file(doc_source_dir, relative_src_file_path)

    create_package_rst_files(algo_pg_dir)


if __name__ == "__main__":
    main()
