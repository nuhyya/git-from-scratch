#!/usr/bin/env python3

import argparse, os, json, sys
import requests
from vctrl.commands.branch import create_branch, list_branches

CONFIG = os.path.expanduser("~/.vctrlcli")

def save_token(token):
    with open(CONFIG, 'w') as f:
        json.dump({"token": token}, f)

def load_token():
    if os.path.exists(CONFIG):
        with open(CONFIG) as f:
            return json.load(f)['token']
    return None

def login(args):
    resp = requests.post(f"{args.server}/login", json={"username": args.username, "password": args.password})
    if resp.status_code == 200:
        token = resp.json()['token']
        save_token(token)
        print("Login successful")
    else:
        print("Login failed")

def push(args):
    from vctrl.remote import push
    push(args.remote, os.getcwd())

def pull(args):
    from vctrl.remote import pull
    pull(args.remote, os.getcwd())

def clone(args):
    from vctrl.remote import clone
    clone(args.remote, args.dest)

def add(args):
    import os
    from vctrl.hash_object import hash_object
    from vctrl.index import add_to_index

    if args.path == ".":
        # Walk through all files recursively
        for root, dirs, files in os.walk(os.getcwd()):
            for fname in files:
                full_path = os.path.join(root, fname)
                if ".vctrl" in full_path:
                    continue  # Skip internal repo files
                with open(full_path, 'rb') as f:
                    data = f.read()
                oid = hash_object(data, write=True)
                rel_path = os.path.relpath(full_path, os.getcwd())
                add_to_index(rel_path, oid)
    else:
        # Single file
        full_path = os.path.join(os.getcwd(), args.path)
        with open(full_path, 'rb') as f:
            data = f.read()
        oid = hash_object(data, write=True)
        add_to_index(args.path, oid)

def commit(args):
    from vctrl.commit import commit
    commit(args.message)

def checkout(args):
    from vctrl.commands.checkout import checkout
    checkout(args.name)

def branch(args):
    if args.name and args.create:
        create_branch(args.name)
    elif args.name:
        print(f"Switching to branch {args.name}")
        checkout(args)
    else:
        list_branches()

def diff(args):
    from vctrl.commands.diff import diff
    diff()

def merge(args):
    from vctrl.commands.merge import merge
    merge(args.base, args.other)

def fetch(args):
    from vctrl.commands.fetch import fetch
    fetch(args.remote)

def init(args):
    from vctrl.repo import init
    init(args.path)

def build_parser():
    parser = argparse.ArgumentParser(prog='vctrl', description="Git-like version control tool")
    subparsers = parser.add_subparsers(title='subcommands', dest='command')

    # login
    login_parser = subparsers.add_parser("login")
    login_parser.add_argument("--server", required=True)
    login_parser.add_argument("--username", required=True)
    login_parser.add_argument("--password", required=True)
    login_parser.set_defaults(func=login)

    # init
    init_parser = subparsers.add_parser("init", help="Initialize a repo")
    init_parser.add_argument("path", nargs='?', default=os.getcwd())
    init_parser.set_defaults(func=init)

    # add
    add_parser = subparsers.add_parser("add", help="Add a file to index")
    add_parser.add_argument("path")
    add_parser.set_defaults(func=add)

    # commit
    commit_parser = subparsers.add_parser("commit", help="Commit changes")
    commit_parser.add_argument("-m", "--message", required=True)
    commit_parser.set_defaults(func=commit)

    # checkout
    checkout_parser = subparsers.add_parser("checkout", help="Checkout branch or commit")
    checkout_parser.add_argument("name")
    checkout_parser.set_defaults(func=checkout)

    # branch
    branch_parser = subparsers.add_parser("branch", help="Create/list/switch branches")
    branch_parser.add_argument("name", nargs="?", help="Branch name")
    branch_parser.add_argument("-b", "--create", action="store_true", help="Create new branch")
    branch_parser.set_defaults(func=branch)

    # diff
    diff_parser = subparsers.add_parser("diff", help="Show diff")
    diff_parser.set_defaults(func=diff)

    # merge
    merge_parser = subparsers.add_parser("merge", help="Merge branches")
    merge_parser.add_argument("base")
    merge_parser.add_argument("other")
    merge_parser.set_defaults(func=merge)

    # fetch
    fetch_parser = subparsers.add_parser("fetch", help="Fetch from remote")
    fetch_parser.add_argument("remote")
    fetch_parser.set_defaults(func=fetch)

    # push
    push_parser = subparsers.add_parser("push", help="Push to remote")
    push_parser.add_argument("remote")
    push_parser.set_defaults(func=push)

    # pull
    pull_parser = subparsers.add_parser("pull", help="Pull from remote")
    pull_parser.add_argument("remote")
    pull_parser.set_defaults(func=pull)

    # clone
    clone_parser = subparsers.add_parser("clone", help="Clone from remote")
    clone_parser.add_argument("remote")
    clone_parser.add_argument("dest")
    clone_parser.set_defaults(func=clone)

    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()

