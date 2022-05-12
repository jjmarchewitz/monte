# TODO: have this file extract the docstrings throughout the repo and put them in API.md
from os import getcwd, sep
from re import findall

# os.chdir()

repo_dir = findall("^.*algo-playground", getcwd())[0]


with open(f"{repo_dir}{sep}doc{sep}TEST.txt", "w") as f:
    f.write("AAA\n")
