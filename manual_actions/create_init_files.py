import os

INIT_FILE_NAME = "__init__.py"


def create_init_file(path, root):
    # create an empty __init__.py file if it does not exist
    init_file = os.path.join(path, INIT_FILE_NAME)
    if not os.path.exists(init_file):
        open(init_file, "w").close()
    # get the list of Python files and directories in the path
    py_files = [fname for fname in os.listdir(path) if fname.endswith(".py") and fname != INIT_FILE_NAME]
    dirs = [dname for dname in os.listdir(path) if os.path.isdir(os.path.join(path, dname)) and dname != "__pycache__"]
    # open the __init__.py file in writte mode
    with open(init_file, "w") as f:
        # if the path is the root path, import all directories
        if path == root:
            for dir_name in dirs:
                f.write(f"from .{dir_name} import *\n")
        # loop through the Python files
        for py_file in py_files:
            # get the module name without the extension
            module_name = py_file[:-3]
            # import the module in the __init__.py file
            f.write(f"from .{module_name} import {module_name}\n")
            # # get the class name is the same as the module name for this case
            # class_name =  module_name  #"".join(word.capitalize() for word in module_name.split("_"))
            # # get the variable name from the module name by making it lowercase and replacing Controller with controller
            # variable_name = module_name.lower().replace("controller", "Controller")
            # # create an instance of the class and assign it to a variable with the variable name
            # f.write(f"{variable_name} = {module_name}()\n")


def create_controllers_init_file():
    thisfolder = os.path.dirname(os.path.abspath(__file__))
    parent_folder = os.path.abspath(os.path.join(thisfolder, os.pardir))
    controllers_path = os.path.abspath(os.path.join(parent_folder, "controllers"))

    print(controllers_path)
    # check if the path exists
    if not os.path.exists(controllers_path):
        print("path does not exist")
    # check if the path is a directory
    if not os.path.isdir(controllers_path):
        print("path is not a directory")
    # walk through the root directory and its subdirectories
    for root, dirs, files in os.walk(controllers_path):
        # create __init__.py files for each directory
        create_init_file(root, controllers_path)


if __name__ == "__main__":
    create_controllers_init_file()
