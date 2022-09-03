#!/usr/bin/env python3

from pathlib import Path
import os
from sys import argv
import subprocess


RS_VERSION = '1.0.0'
BUILD_DIR = './bs'

def info(message: str) -> str:
  return message

def error(message: str) -> str:
  return f'\033[38;2;168;50;72m{message}\033[0m'

def bold(message: str) -> str:
  return f'\033[1m{message}\033[0m'


helpfile = f"""
rs: tiny build system

Usage:
  rs <command> [<args>]
  rs [<default-command-args>]
  rs ls

Description:
  Rs is a build-system that runs scripts in a folder.

  1. Create a {BUILD_DIR} directory in your repository root

  2. Add commands by adding executable scripts (with shebangs) with to {BUILD_DIR} with
  the name of the command. For example

  > rs publish

  will call:

  > {BUILD_DIR}/publish[extension]

  3. Additional arguments can be passed to your command. For example,

  > rs publish --stage production --verbose

  will call:

  > {BUILD_DIR}/publish --stage production --verbose

  4. You can define a default script at {BUILD_DIR}/default[extension] which will
  be called when the argument passed for <command> doesn't match any
  script in {BUILD_DIR}

  For example, if 'restore' does not have a matching script,

  > rs restore --previous

  will call

  > {BUILD_DIR}/restore restore --previous

See Also:
  rs is a python-based clone of bs <https://github.com/labaneilers/bs>, with
  a few added features.
"""

def show_rs_help():
  for line in helpfile.splitlines():
    if line.strip().startswith('> '):
      print(bold(line))
    else:
      print(info(line))


def list_commands():
  for file in sorted(os.listdir(BUILD_DIR)):
    execable = os.access(os.path.join(BUILD_DIR, file), os.X_OK)

    if execable:
      print(f"- {BUILD_DIR}/{file}*")
    else:
      print(f"- {BUILD_DIR}/{file}")


def get_script_path(command: str) -> str:
  match = None

  for file in os.listdir(BUILD_DIR):
    name = os.path.basename(file)
    if name == command:
      match = os.path.join(os.path.join(BUILD_DIR, file))
      break

    name_no_ext = Path(name).with_suffix('').stem
    if name_no_ext == command:
      match = os.path.join(os.path.join(BUILD_DIR, file))
      break

  if not match:
    match = os.path.join(BUILD_DIR, 'default')

  if not os.path.isfile(match):
    if match == os.path.join(BUILD_DIR, 'default'):
      message = f"rs: no file found for '{command}' and default-executable '{BUILD_DIR}/default' is also missing."

      if command == 'list':
        message = message + ' Did you mean "rl ls"?'
      else:
        message = message + ' Please create one of these files.'

      print(message)
    else:
      print(error(f"rs: command '{command}' could not be executed as {match} does not exist"))

    exit(1)

  if not os.access(match, os.X_OK):
    print(error(f"rs: command '{command}' could not be executed as {match} is not marked as executable"))
    exit(1)

  return match


def main():
  if len(argv) < 2:
    show_rs_help()
    return

  command = argv[1]

  if command in {'help', '--help', 'h'}:
    show_rs_help()
    return

  if command in {'--version', 'v'}:
    print(RS_VERSION)
    return

  if not os.path.isdir(BUILD_DIR):
    print(error(f"rs: Expected a build-commands directory at {BUILD_DIR}, but none was found"))
    exit(1)

  if command == "ls":
    print("rs: Available rs commands for this project (executables marked with *)")

    list_commands()
    exit(0)

  subargs = argv[2:]

  script_path = get_script_path(command)
  instance = subprocess.run([script_path] + subargs)

  exit(instance.returncode)


main()
