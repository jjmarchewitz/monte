# TODO: have this file extract the docstrings throughout the repo and put them in API.md

# TODO: Extract all of the TODO: markers in the repository and put them into TODO.md,
# sorted if possible

import ast
import os
from re import findall


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


def main():
    repo_dir = findall("^.*algo-playground", os.getcwd())[0]
    src_dir = f"{repo_dir}{os.sep}src"

    py_src_files_list = find_python_source_files_in_dir(src_dir)

    print(py_src_files_list)

    for src_file_path in py_src_files_list:

        module_name = os.path.basename(src_file_path)

        with open(src_file_path, "r") as src_file:
            code = ast.parse(src_file.read())

        # Holy shit I cannot believe I am using ASTs for something. Still, fuck SW2.
        for node in ast.walk(code):

            if isinstance(node, ast.FunctionDef):

                docstring = ast.get_docstring(node)
                if docstring:
                    print(f"FN in {module_name}: {node.name}\n{repr(docstring)}\n\n")
                else:
                    print(f"FN in {module_name}: {node.name}\n\n")

            # elif isinstance(node, ast.ClassDef):
            #     print(f"CL: {repr(node)}")

            # Modules don't have a "name" attribute
            # elif isinstance(node, ast.Module):
            #     print(f"MD: {repr(node)}")

    with open(f"{repo_dir}{os.sep}doc{os.sep}API.md", "w") as f:
        f.write("# API Documentation for algo-playground \n")


if __name__ == "__main__":
    main()
