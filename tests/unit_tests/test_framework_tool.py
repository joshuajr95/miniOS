#! /usr/bin/python3


from typing import List
import re
import sys
import os
import argparse
import json







def get_test_dirs() -> List[str]:

	subdirs: List[str] = []

	for f in os.scandir():
		if f.is_dir() and not f.name.startswith(".") and f.name != "obj":
			subdirs.append(f.name)

	return subdirs



def get_test_group_name(subdir: List[str]) -> None:
	return f"{subdir}_GROUP"



'''
The UNIT_TEST macro must be at the beginning of line and the test
function header must be the rest of the line.
'''
def generate_test_function_list_from_test_file(test_file: str) -> List[str]:

	test_functions: List[str] = []
	in_block_comment: bool = False

	with open(test_file, "r") as file_handle:

		i: int = 0
		for line in file_handle:

			i += 1

			if re.search(r"//", line) is not None:
				continue

			if re.search(r"/\*", line):
				in_block_comment = True

			if re.search(r"\*/", line) is not None:
				in_block_comment = False


			# grab the function name and append it to test_functions
			if re.search("UNIT_TEST", line) is not None and not in_block_comment:
				test_functions.append(line.strip().split(" ")[2][:-2])


	return test_functions


def generate_test_group_file_from_test_function_list(manifest_file: str, tests: List[str], folder: str) -> None:

	header_file_name: str = f"{folder}/" + manifest_file + ".h"
	c_file_name: str = f"{folder}/" + manifest_file + ".c"


	with open(header_file_name, "w") as file_handle:

		include_guard: str = manifest_file.replace(".", "_").upper()

		# write opening of include guard
		file_handle.write(f"#ifndef {include_guard}\n")
		file_handle.write(f"#define {include_guard}\n")

		# generate declarations to prevent errors
		for test_func in tests:
			file_handle.write(f"bool {test_func}();\n")


		file_handle.write(f"test_group_t {folder}_test_group;\n\n\n")

		file_handle.write("#endif\n")



	with open(c_file_name, "w") as file_handle:

		# generate warning and help message
		file_handle.write("// THIS FILE IS AUTO-GENERATED. DO NOT EDIT!!!\n")
		file_handle.write("// See generate_tests.py for details\n\n\n")


		# make sure include paths are working properly
		file_handle.write("#include \"test.h\"\n")
		file_handle.write("#include \"../test_group.h\"\n")
		file_handle.write(f"#include \"{manifest_file}.h\"\n\n\n")

		file_handle.write("#include <stdbool.h>\n\n\n")



		# generate test function name mapping
		file_handle.write(f"char *{folder}_test_function_names[] = {{\n")

		for test_func in tests:
			file_handle.write(f"\t\"{test_func}\",\n")

		file_handle.write("};\n\n")


		# generate test manifest
		file_handle.write(f"test_function {folder}_tests_to_run[] = {{\n")

		for test_func in tests:
			file_handle.write(f"\t{test_func},\n")

		file_handle.write("};\n\n\n")


		file_handle.write(f"test_group_t {folder}_test_group = {{\n")
		file_handle.write(f"\t.funcs = &{folder}_tests_to_run[0],\n")
		file_handle.write(f"\t.func_names = &{folder}_test_function_names[0],\n")
		file_handle.write(f"\t.num_tests = {len(tests)},\n")
		file_handle.write(f"\t.group_name = \"{folder}_test_group\"\n")
		file_handle.write("};\n\n\n")




def generate_test_group_list(subdirs: List[str]) -> List[str]:

	#subdirs: List[str] = get_test_dirs()
	test_groups: List[str] = []

	for dir in subdirs:
		group_name: str = get_test_group_name(dir)
		test_group_file: str = dir + f"/{group_name}.c"
		if os.path.exists(test_group_file):
			test_group_name: str = dir + "_test_group"
			test_groups.append(test_group_name)

	return test_groups




def generate_manifest_file_from_test_group_list(manifest_file: str, test_groups: List[str]) -> None:
	
	with open(manifest_file, "w") as file_handle:

		# generate warning and help message
		file_handle.write("// THIS FILE IS AUTO-GENERATED. DO NOT EDIT!!!\n")
		file_handle.write("// See generate_tests.py for details\n\n\n")


		file_handle.write("#include \"test.h\"\n\n\n")


		subdirs: List[str] = get_test_dirs()


		#for dir in subdirs:
		#	group_name: str = get_test_group_name(dir)
		#	file_handle.write(f"#include \"{dir}/{group_name}.h\"\n")

		#file_handle.write("\n\n")



		for group in test_groups:
			file_handle.write(f"extern test_group_t {group};\n")

		file_handle.write("\n\n")

		file_handle.write("test_group_t *test_groups_to_run[] = {\n")

		for group in test_groups:
			file_handle.write(f"\t&{group},\n")

		file_handle.write("};\n\n")

		file_handle.write(f"int num_test_groups = {len(test_groups)};\n\n\n")



def create_submake(subfolder: str):
	with open(f"{subfolder}/tests.mk", "w") as f:

		f.write("\n\n# CC, CFLAGS, GEN_TEST_SCRIPT, OBJ_DIR, SUBTARGET, SHELL, SUBGOALS, SUB_OBJS, and OBJS\n")
		f.write("# are all exported from top-level Makefile\n\n\n")

		f.write("CURRENT_DIR=$(shell basename $$(pwd))\n")
		f.write("TEST_GROUP_NAME=$(CURRENT_DIR)_GROUP\n")
		f.write("TEST_GROUP_FILE=$(patsubst %, %.c, $(TEST_GROUP_NAME))\n")
		f.write("TEST_GROUP_HEADER=$(patsubst %, %.h, $(TEST_GROUP_NAME))\n\n")
		f.write("INCLUDE_PATHS += -I..\n\n\n\n\n")

		f.write("SRCS = $(shell cd .. ; ./test_framework_tool.py get_source_file_paths $(CURRENT_DIR); cd $(CURRENT_DIR))\n")
		f.write(f"TEST_SRCS =\ttest_{subfolder}.c\t\t\t\\\n")
		f.write("\t\t\t$(TEST_GROUP_FILE)\n\n\n")

		f.write("TEST_OBJS = $(patsubst %.c, ../$(OBJ_DIR)/$(CURRENT_DIR)/%.o, $(TEST_SRCS))\n")
		f.write("OBJS = $(patsubst %.c, %.o, $(SRCS))\n\n\n\n\n")

		f.write("########################\n")
		f.write("# Targets for sub-make #\n")
		f.write("########################\n\n")
		f.write(".PHONY: clean setup\n\n\n")

		f.write("$(SUBTARGET): setup $(OBJS) $(TEST_OBJS)\n\n\n")

		f.write("# create subfolder in object file folder for this folder's object files\n")
		f.write("setup:\n")
		f.write("\tif [ ! -d ../$(OBJ_DIR)/$(CURRENT_DIR) ]; then mkdir ../$(OBJ_DIR)/$(CURRENT_DIR); fi\n\n")

		f.write("$(OBJS): %.o: %.c\n")
		f.write("\t$(CC) $(CFLAGS) $(INCLUDE_PATHS) -c $< -o ../$(OBJ_DIR)/$(CURRENT_DIR)/$$(basename $@)\n\n\n\n")

		f.write("$(TEST_OBJS): ../$(OBJ_DIR)/$(CURRENT_DIR)/%.o: %.c\n")
		f.write("\t$(CC) $(CFLAGS) $(INCLUDE_PATHS) -c $< -o $@\n\n\n")

		f.write("clean:\n")
		f.write("\tif [ -e $(TEST_GROUP_FILE) ]; then rm $(TEST_GROUP_FILE); fi\n")
		f.write("\tif [ -e $(TEST_GROUP_HEADER) ]; then rm $(TEST_GROUP_HEADER); fi\n\n\n\n")







		


def generate_test_group(subfolder: str) -> None:

	# get the list of test directories
	subdirs: List[str] = get_test_dirs()

	if subfolder.endswith("/"):
		subfolder = subfolder[:-1]

	# check that the test directory exists
	if subfolder not in subdirs:
		print(f"Specified subfolder: {subfolder} does not exist")
		print(f"Subdirectories: {subdirs}.")
		return


	# get the name of the file with unit test functions
	test_file_name: str = subfolder + "/test_" + subfolder + ".c"

	# get the name of the output group file
	test_group_file_name: str = get_test_group_name(subfolder)

	# get the test function list and write it to the test group file
	test_functions: List[str] = generate_test_function_list_from_test_file(test_file_name)
	generate_test_group_file_from_test_function_list(test_group_file_name, test_functions, subfolder)



def generate_group_list(groups: List[str]):
	test_groups: List[str] = generate_test_group_list(groups)
	generate_manifest_file_from_test_group_list("test.c", test_groups)



def create_test_package(subfolder: str) -> None:

	with open("test_packages.json", "r") as f:
		package_object = json.load(f)

		if subfolder in package_object["packages"]:
			print(f"Package \"{subfolder}\" already exists...")
			return



	if os.path.exists(subfolder):
		print(f"Package name {subfolder} conflicts with already existing path. Please choose another name.")
		return


	print(f"Creating package \"{subfolder}\"...")

	# create the package and contents
	os.mkdir(subfolder)

	with open(f"{subfolder}/test_{subfolder}.c", "w") as fp:
		pass


	# create and populate sub-makefile {subfolder}/tests.mk
	create_submake(subfolder)


	# write package manifest JSON file
	package_object = {
		"name": f"{subfolder}",
		"unit_test_files": [
			f"test_{subfolder}.c"
		],
		"source_files": []
	}

	with open(f"{subfolder}/package.json", "w") as f:
		json.dump(package_object, f, indent=4)



	# add package to package list in JSON file
	with open("test_packages.json", "r+") as f:
		package_object = json.load(f)
		package_object["packages"].append(f"{subfolder}")

		f.seek(0)
		json.dump(package_object, f, indent=4)
		f.truncate()





def remove_test_package(subfolder: str) -> None:

	with open("test_packages.json", "r") as f:
		package_object = json.load(f)

		if subfolder not in package_object["packages"]:
			print(f"Package \"{subfolder}\" does not exist or is not a package...")
			return


	if not os.path.exists(subfolder):
		print(f"Package folder {subfolder} does not appear to exist.")
		return


	print(f"Removing package \"{subfolder}\"...")

	for file in os.listdir(subfolder):
		os.remove(f"{subfolder}/{file}")

	os.rmdir(subfolder)

	with open("test_packages.json", "r+") as f:
		package_object = json.load(f)
		package_object["packages"].remove(subfolder)

		f.seek(0)
		json.dump(package_object, f, indent=4)
		f.truncate()



'''
File path must be relative to root directory.
'''
def add_source_file(subfolder: str, file_path: str):

	root_dir: str = None
	
	with open("test_packages.json", "r") as f:
		package_object = json.load(f)

		if subfolder not in package_object["packages"]:
			print(f"Package \"{subfolder}\" does not exist or is not a package...")
			return

		root_dir = package_object["root"]
	
	if not os.path.exists(root_dir + "/" + file_path):
		print(f"File: {file_path} does not appear to exist in project with root directory {root_dir}...")
		return
	
	with open(f"{subfolder}/package.json", "r") as f:
		package_object = json.load(f)
		if file_path in package_object["source_files"]:
			print(f"File: {file_path} has already been added to test package {subfolder}")
			return
	
	print(f"Adding file {file_path} to test package {subfolder}...")
	
	with open(f"{subfolder}/package.json", "r+") as f:
		package_object = json.load(f)
		package_object["source_files"].append(file_path)

		f.seek(0)
		json.dump(package_object, f, indent=4)
		f.truncate()

	

def set_root_dir(root: str):

	with open("test_packages.json", "r+") as f:
		package_object = json.load(f)
		package_object["root"] = root

		f.seek(0)
		json.dump(package_object, f, indent=4)
		f.truncate()


def get_source_file_paths(subfolder: str):

	paths: List[str] = []
	out_str: str = ""
	root: str = None

	with open("test_packages.json", "r") as f:
		package_object = json.load(f)
		root = package_object["root"]
	
	with open(f"{subfolder}/package.json", "r") as f:
		package_object = json.load(f)

		for file in package_object["source_files"]:
			path: str = root + "/" + file
			paths.append(path)
	

	for path in paths:
		out_str = out_str + path + " "
	
	print(out_str)


def get_test_packages() -> None:

	packages: List[str] = []
	out_str: str = ""

	with open("test_packages.json", "r") as f:
		package_object = json.load(f)

		for package in package_object["packages"]:
			packages.append(package)
	

	for package in packages:
		out_str = out_str + package + " "
	
	print(out_str)


def main() -> None:


	# add argparser
	parser = argparse.ArgumentParser(description="generate unit tests and groups for miniOS")
	subparsers = parser.add_subparsers(dest="command")

	# sub-parser for the generate_group command
	group_parser = subparsers.add_parser("generate_group", help="Generate a single test group")
	group_parser.add_argument("subfolder")

	# sub-parser for the create_test_package command
	create_package_parser = subparsers.add_parser("create_test_package", help="Creates a unit test package with the given name")
	create_package_parser.add_argument("subfolder")

	# sub-parser for the remove_test_package command
	remove_package_parser = subparsers.add_parser("remove_test_package", help="Removes a unit test package with the given name")
	remove_package_parser.add_argument("subfolder")

	# sub-parser for the add_source_file command
	add_source_file_parser = subparsers.add_parser("add_source_file", help="Adds the given source file to the given package. Source file path must be relative to source tree root directory.")
	add_source_file_parser.add_argument("subfolder")
	add_source_file_parser.add_argument("file_path")

	# sub-parser for the get_source_file_paths command
	get_file_paths_parser = subparsers.add_parser("get_source_file_paths", help="Gets the paths to all the source files for a given package.")
	get_file_paths_parser.add_argument("subfolder")

	# sub-parse for the set_root_dir command
	set_root_parser = subparsers.add_parser("set_root_dir", help="Configures the root directory of the project.")
	set_root_parser.add_argument("root")

	# sub-parser for the generate_group_list command
	test_list_parser = subparsers.add_parser("generate_group_list", help="Generate the top-level test apparatus. Must be run after generate_group.")
	test_list_parser.add_argument("groups", nargs="+")

	# sub-parser for getting the test packages
	test_package_parser = subparsers.add_parser("get_test_packages", help="Gets the names of all test packages")

	args = parser.parse_args()


	if args.command == "generate_group":
		generate_test_group(args.subfolder)

	elif args.command == "generate_group_list":
		generate_group_list(args.groups)

	elif args.command == "create_test_package":
		create_test_package(args.subfolder)

	elif args.command == "remove_test_package":
		remove_test_package(args.subfolder)
	
	elif args.command == "add_source_file":
		add_source_file(args.subfolder, args.file_path)
	
	elif args.command == "get_source_file_paths":
		get_source_file_paths(args.subfolder)
	
	elif args.command == "set_root_dir":
		set_root_dir(args.root)
	
	elif args.command == "get_test_packages":
		get_test_packages()

	else:
		print(f"Subcommand: {args.command} not recognized")



	return




if __name__ == "__main__":
	main()


