# rs: simple build system

Rs is a minimal, no-dependency build-system cloned from [bs](https://github.com/labaneilers/bs).

## Usage

```sh
rs ls
rs <command> [<args>]
rs [<default-command-args>]
```

Create a folder called `bs`, and put [executable CLI files](https://unix.stackexchange.com/questions/291217/what-does-the-argument-x-means-in-unix-regarding-permissions) written in any language in it.

```
bs
├───build
├───install.py
├───run.ts
└───test
```

Then run these commands directly:

`./run.ts myargs --my-flags`

Or use `rs` build to remove a few keystrokes.

`rs run myargs --my-flags`

Use tab-completions to save more typing; it'll suggest your workspace's commands.

Use

`rs :x`

to set scripts in the directory to executable

or

`rs :ls`

to list known commands. That's it!

## Installation

```
sudo cp rs.py /usr/bin/rs
```

Add this to your `.zshrc`

```
eval "$(rs :completion-zsh)"
```

## License

The MIT License

Copyright (c) 2026 Róisín Grannell

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
