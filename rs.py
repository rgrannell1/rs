#!/usr/bin/env python3

from pathlib import Path
import os
import stat
from sys import argv
import subprocess
import sys


RS_VERSION = "2.0.0"
BUILD_DIR = "./bs"
NEWLINE = "\n"
BUILD_DIRECTORY_EXISTS = os.path.isdir(BUILD_DIR)

# Register ZSH completions by inspecting the bs directory
ZSH_COMPLETION_SCRIPT = r"""
_rs_complete() {
  local -a cmds
  cmds=("${(@f)$(rs :completions)}")

  compadd -a cmds
}

compdef _rs_complete rs
"""

# Register Bash completions by inspecting the bs directory
BASH_COMPLETION_SCRIPT = r"""
_rs_complete() {
  local cur="${COMP_WORDS[COMP_CWORD]}"
  local -a words

  while IFS= read -r line; do
    [[ -n $line ]] && words+=("$line")
  done < <(rs :completions 2>/dev/null)
  COMPREPLY=($(compgen -W "${words[*]}" -- "$cur"))
}

complete -F _rs_complete rs
"""

# Why not save someone googling them?
COMMON_SHEBANGS = '\n'.join([line for line in [
    "#! /usr/bin/env python3",
    "#! /usr/bin/env sh",
    "#! /usr/bin/env zsh",
]])

def validate_build_directory() -> None:
    """Check that the build directory actually exists"""

    if not os.path.isdir(BUILD_DIR):
        eprint(
            error(
                f"rs: Expected a build-commands directory at {BUILD_DIR}, but none was found"
            )
        )
        exit(1)


def info(message: str) -> str:
    """Print an info level message"""

    return message


def error(message: str) -> str:
    """Return an error level message"""

    return f"\033[38;2;168;50;72m{message}\033[0m"


def bold(message: str) -> str:
    """Return a bold message"""

    return f"\033[1m{message}\033[0m"


def blue(message: str) -> str:
    """Return a blue message"""

    return f"\033[0;34m{message}\033[0m"


def list_commands(simple: bool = False) -> list[str]:
    """List formatted descriptions of each command in the build directory."""

    out: list[str] = []

    for file in sorted(os.listdir(BUILD_DIR)):
        name = Path(file).stem
        execable = os.access(os.path.join(BUILD_DIR, file), os.X_OK)

        # in simple mode, just give the names of the commands without formatting
        if simple:
            out.append(name)
            continue

        if execable:
            out.append(blue(f"rs {name}"))
        else:
            out.append(f"rs {name}")

    return out


def get_help_commands() -> str:
    """Get the commands that can be used in the help message"""

    if not BUILD_DIRECTORY_EXISTS:
        return f"  No commands found, create a {BUILD_DIR} directory to get started"

    return NEWLINE.join(f"  {comm}" for comm in list_commands())


HELPFILE = f"""
rs: tiny build system

Current Workspace Commands:

{get_help_commands()}

Usage:
  rs <command> [<args>]
  rs :x
  rs :ls
  rs [<default-command-args>]

Description:
  Rs is a build-system that runs scripts in a folder. Add a shebang line, and we'll use that language.

  1. Create a {BUILD_DIR} directory in your repository root

  2. Add commands by adding executable scripts to {BUILD_DIR} with
  the name of the command. For example

  > rs publish

  will call:

  > {BUILD_DIR}/publish<extension>

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

  > {BUILD_DIR}/default restore --previous

Special Commands:
  :x  - change script permissions to executable
  :ls - list current workspace commands
  :completions     - list command names (one per line, for scripts)
  :completion-zsh  - print zsh completion script; add eval "$(rs :completion-zsh)" to .zshrc
  :completion-bash - print bash completion script; add eval "$(rs :completion-bash)" to .bashrc

See Also:
  rs is a python-based clone of bs <https://github.com/labaneilers/bs>, with
  a few added features.
"""


def eprint(message: str) -> None:
    """Print to stderr"""

    print(message, file=sys.stderr)


def show_rs_help() -> None:
    """Apply ANSI formatting to the help text"""

    for line in HELPFILE.splitlines():
        if line.strip().startswith("> "):
            eprint(bold(line))
        else:
            eprint(info(line))


def get_script_path(command: str) -> str:
    """Get the path to the script that matches the command, or the default script if no match is found"""

    # check for matching names with and without extensions
    for file in os.listdir(BUILD_DIR):
        if file == command:
            return os.path.join(BUILD_DIR, file)

        name_no_ext = Path(file).with_suffix("").stem
        if name_no_ext == command:
            return os.path.join(BUILD_DIR, file)

    # no matching file found; fall back to `default` instead
    return os.path.join(BUILD_DIR, "default")


def validate_script(command: str, fpath: str) -> None:
    """Check the script is something that exists we can run"""

    # handle missing files
    if not os.path.isfile(fpath):
        if fpath == os.path.join(BUILD_DIR, "default"):
            eprint(
                f"rs: no file found for '{command}' and default-executable '{BUILD_DIR}/default' is also missing."
                " Please create one of these files."
            )
        else:
            eprint(
                error(
                    f"rs: command '{command}' could not be executed as {fpath} does not exist"
                )
            )

        exit(1)

    # Check executable
    if not os.access(fpath, os.X_OK):
        eprint(
            error(
                f"rs: command '{command}' could not be executed as {fpath} is not marked as executable"
            )
        )
        exit(1)

    # Check shebang line
    with open(fpath) as file:
        first_line = file.readline()

    if not first_line.startswith("#!"):
        eprint(error(f"rs: command '{command}' is missing a shebang line. Common shebang lines are\n{COMMON_SHEBANGS}"))
        exit(1)


def run_special_command(command: str) -> None:
    """Run a special internal commands"""

    if command == "x":
        change_permissions_mode()
        return
    elif command == "ls":
        for comm in list_commands():
            eprint(comm)
        return
    elif command == "completions":
        for comm in list_commands(simple=True):
            print(comm)
    elif command == "completion-zsh":
        print(ZSH_COMPLETION_SCRIPT, end="")
        return
    elif command == "completion-bash":
        print(BASH_COMPLETION_SCRIPT, end="")
        return
    else:
        eprint(error(f"rs: unknown special command: {command}"))
        exit(1)


def change_permissions_mode() -> None:
    """Change script permissions to executable"""

    for file in os.listdir(BUILD_DIR):
        fpath = os.path.join(BUILD_DIR, file)

        if os.path.isfile(fpath) and not os.access(fpath, os.X_OK):
            # chmod +x
            st = os.stat(fpath)
            os.chmod(fpath, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

            eprint(f"rs: changed permissions of {fpath} to executable")


def main() -> None:
    # too few arguments; show docs
    if len(argv) < 2:
        show_rs_help()
        return

    command = argv[1]

    if command in {"help", "--help", "h"}:
        show_rs_help()
        return

    if command in {"--version", "v"}:
        eprint(RS_VERSION)
        return

    validate_build_directory()

    if command.startswith(":"):
        command = command[1:]
        run_special_command(command)
        return

    # subprocess out to the subcommand, and pass additional arguments to the subcommand
    script_path = get_script_path(command)
    validate_script(command, script_path)

    instance = subprocess.run([script_path] + argv[2:])

    exit(instance.returncode)


if __name__ == "__main__":
    main()
