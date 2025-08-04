# vctrl — A Git-Inspired Version Control System

`vctrl` is a simplified, educational version control system built with Python. It mimics key functionalities of Git, including tracking file changes, managing commits, creating branches, and merging — all from the command line.

---

## Features

- Initialize a new repository
- Track file changes and stage them
- Commit snapshots of your project
- View diffs between commits and working directory
- Create and switch between branches
- Merge branches (basic functionality)

--

## Installation

```bash
git clone https://github.com/yourusername/vctrl.git
cd vctrl
pip install .
```
--
## Architecture
```
                       +-----------------------+
                       |     User / CLI        |
                       |  vctrl <command>      |
                       +----------+------------+
                                  |
                                  v
                     +------------+------------+
                     |        CLI Parser       |
                     |      (cli.py)           |
                     +------------+------------+
                                  |
     +----------------------------+------------------------------+
     |                            |                              |
     v                            v                              v
+------------+       +-----------------------+        +-----------------+
| repo.py    |       | commands/* (branch,   |        | refs.py         |
| Repo Mgmt  |       | checkout, merge, etc) |        | Ref handling    |
+------------+       +-----------------------+        +-----------------+
     |                                                          |
     v                                                          v
+------------+                                         +-----------------+
| index.py   |<--------------------------------------->| objects.py      |
| Staging    |           Reads/Writes objects         | Object store    |
+------------+                                         +-----------------+
                                                          |
                                                          v
                                                  +---------------+
                                                  | .vctrl/       |
                                                  | Object store  |
                                                  | Index, HEAD   |
                                                  +---------------+
```
--
## Usage 
```bash
vctrl init               # Initialize a new vctrl repository
vctrl add <file>         # Stage a file
vctrl commit -m "msg"    # Commit staged files
vctrl diff               # Show working directory changes
vctrl branch <name>      # Create a new branch
vctrl checkout <branch>  # Switch to a branch
vctrl merge <branch>     # Merge branch into current
```
--
## Project Structure 
```bash
vctrl/
├── cli.py           # Command-line interface logic
├── repo.py          # Repo initialization and configuration
├── refs.py          # HEAD, branches, and tag references
├── index.py         # Index (staging area) management
├── objects.py       # Object storage (blobs, trees, commits)
├── commands/
    ├── branch.py
    ├── checkout.py
    ├── diff.py
    └── merge.py
```
--
## Design Principles
Built using only Python standard library (argparse, hashlib, zlib, os, etc.)

Mimics Git object model (blobs, trees, commits)

Simplified implementation for learning 

--
This project is a hands-on tool for understanding how Git works internally:

SHA-1 object hashing

Staging/index file

Tree and commit objects

References (HEAD, branches)

Checkout and merge mechanics



