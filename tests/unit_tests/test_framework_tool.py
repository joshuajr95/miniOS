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




def generate_test_group_list() -> List[str]:

	subdirs: List[str] = get_test_dirs()
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
		f.write("TEST_GROUP_FILE=$(patsubst %, %.c, $(TEST_GROUP_NAME))\n")
		f.write("TEST_GROUP_HEADER=$(patsubst %, %.h, $(TEST_GROUP_NAME))\n\n")
		f.write("INCLUDE_DIRS=..\n\n\n\n\n")

		f.write("#########################\n")
		f.write("# Add source files here #\n")
		f.write("#########################\n\n")

		f.write(f"SRCS =\ttest_{subfolder}.c\t\t\t\\\n")
		f.write("\t\t$(TEST_GROUP_FILE)\n\n\n")

		f.write("OBJS = $(patsubst %.c, ../$(OBJ_DIR)/$(CURRENT_DIR)/%.o, $(SRCS))\n\n\n\n\n")

		f.write("########################\n")
		f.write("# Targets for sub-make #\n")
		f.write("########################\n\n")
		f.write(".PHONY: clean setup\n\n\n")

		f.write("$(SUBTARGET): setup $(OBJS)\n\n\n")

		f.write("# create subfolder in object file folder for this folder's object files\n")
		f.write("setup:\n")
		f.write("\tif [ ! -d ../$(OBJ_DIR)/$(CURRENT_DIR) ]; then mkdir ../$(OBJ_DIR)/$(CURRENT_DIR); fi\n\n")

		f.write("$(OBJS): ../$(OBJ_DIR)/$(CURRENT_DIR)/%.o: %.c\n")
		f.write("\t$(CC) $(CFLAGS) -I$(INCLUDE_DIRS) -c $< -o $@\n\n\n\n")

		f.write("clean:\n")
		f.write("\tif [ -e $(TEST_GROUP_FILE) ]; then rm $(TEST_GROUP_FILE); fi\n")
		f.write("\tif [ -e $(TEST_GROUP_HEADER) ]; then rm $(TEST_GROUP_HEADER); fi\n\n\n\n")







		


def generate_test_group(subfolder: str) -> None:

	# get the list of test directories
	subdirs: List[str] = get_test_dirs()

	# check that the test directory exists
	if subfolder not in subdirs:
		print(f"Specified subfolder: {subfolder} does not exist")
		return


	# get the name of the file with unit test functions
	test_file_name: str = subfolder + "/test_" + subfolder + ".c"

	# get the name of the output group file
	test_group_file_name: str = get_test_group_name(subfolder)

	# get the test function list and write it to the test group file
	test_functions: List[str] = generate_test_function_list_from_test_file(test_file_name)
	generate_test_group_file_from_test_function_list(test_group_file_name, test_functions, subfolder)



def generate_group_list():

	test_groups: List[str] = generate_test_group_list()
	generate_manifest_file_from_test_group_list("test.c", test_groups)



def create_test_package(subfolder: str) -> None:

	# check if package already in test_packages.json
		# if so, print error and return
	# check if package path already exists
		# if so
			# print that path already exists, choose another name, return

	# create package folder
	# create test_<package_name>.c file
	# create tests.mk
	# create package.json

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
		]
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




def main() -> None:


	# add argparser
	parser = argparse.ArgumentParser(description="generate unit tests and groups for miniOS")
	subparsers = parser.add_subparsers(dest="command")

	# sub-parser for the generate_group command
	group_parser = subparsers.add_parser("generate_group", help="Generate a single test group")
	group_parser.add_argument("subfolder")

	# sub-parser for the create_test_package command
	group_parser = subparsers.add_parser("create_test_package", help="Creates a unit test package with the given name")
	group_parser.add_argument("subfolder")

	# sub-parser for the remove_test_package command
	group_parser = subparsers.add_parser("remove_test_package", help="Removes a unit test package with the given name")
	group_parser.add_argument("subfolder")

	# sub-parser for the generate_group_list command
	test_parser = subparsers.add_parser("generate_group_list", help="Generate the top-level test apparatus. Must be run after generate_group.")

	args = parser.parse_args()


	if args.command == "generate_group":
		generate_test_group(args.subfolder)

	elif args.command == "generate_group_list":
		generate_group_list()

	elif args.command == "create_test_package":
		create_test_package(args.subfolder)

	elif args.command == "remove_test_package":
		remove_test_package(args.subfolder)

	else:
		print(f"Subcommand: {args.command} not recognized")



	return




if __name__ == "__main__":
	main()


