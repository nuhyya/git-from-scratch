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
    try:
        resp = requests.post(f"{args.server}/login", json={
            "username": args.username,
            "password": args.password
        })
        if resp.status_code == 200:
            token = resp.json()['token']
            save_token(token)
            print("Login successful")
        else:
            print("Login failed:", resp.text)
    except requests.exceptions.RequestException as e:
        print("Server error:", e)

def status(args):
    from vctrl.refs import get_ref, get_branch_name
    branch = get_branch_name()
    if branch:
        print(f"📍 You are on branch: {branch}")
    else:
        from vctrl.refs import get_ref
        commit_oid = get_ref("HEAD")
        print(f"📍 HEAD detached at {commit_oid[:7]}")

def push(args):
    from vctrl.remote import push
    push(args.remote, os.getcwd())
    print(f"Pushed to {args.remote}")

def pull(args):
    from vctrl.remote import pull
    pull(args.remote, os.getcwd())
    print(f"Pulled from {args.remote}")

def clone(args):
    from vctrl.remote import clone
    clone(args.remote, args.dest)
    print(f"Cloned from {args.remote} into {args.dest}")

def add(args):
    from vctrl.objects import hash_object
    from vctrl.index import add_to_index

    def process_file(path):
        with open(path, 'rb') as f:
            data = f.read()
        oid = hash_object(data, type_="blob")
        rel_path = os.path.relpath(path, os.getcwd())
        add_to_index(rel_path, oid)
        print(f"Added {rel_path} ({oid[:7]})")

    if args.path == ".":
        for root, dirs, files in os.walk(os.getcwd()):
            if '.vctrl' in root:
                continue
            for fname in files:
                full_path = os.path.join(root, fname)
                if ".vctrl" in full_path:
                    continue
                process_file(full_path)
    else:
        full_path = os.path.join(os.getcwd(), args.path)
        if os.path.isfile(full_path):
            process_file(full_path)
        else:
            print(f"File not found: {args.path}")

def commit(args):
    from vctrl.objects import Commit, write_tree
    from vctrl.refs import get_ref, update_ref, get_ref_path
    from vctrl.objects import get_object
    from vctrl.repo import repo_path

    message = args.message.strip()
    if not message:
        print("Commit message cannot be empty.")
        return

    tree_oid = write_tree()
    if not tree_oid:
        print("Nothing to commit.")
        return

    parent = get_ref("HEAD")
    if parent:
        parent_commit = get_object(parent, expected_type="commit").decode()
        for line in parent_commit.splitlines():
            if line.startswith("tree "):
                parent_tree_oid = line.split()[1]
                if parent_tree_oid == tree_oid:
                    print("No changes since last commit.")
                    return
                break

    author_name = os.environ.get("GIT_AUTHOR_NAME", "you")
    author_email = os.environ.get("GIT_AUTHOR_EMAIL", "notknown")

    commit_obj = Commit(tree_oid=tree_oid, parent=parent,
                        message=message,
                        author_name=author_name,
                        author_email=author_email)
    oid = commit_obj.save()

    head = os.path.join(repo_path(), "HEAD")
    with open(head) as f:
        ref = f.read().strip()
    if ref.startswith("ref:"):
        update_ref(ref[5:], oid)  # write to branch ref
    else:
        update_ref("HEAD", oid)
    print(f"Committed: {oid[:7]}")

def checkout_branch(args):
    from vctrl.commands.checkout import checkout
    checkout(args.name)
    print(f"Checked out {args.name}")

def handle_branch(args):
    if args.name and args.create:
        create_branch(args.name)
        print(f"Created branch {args.name}")
    elif args.name:
        print(f"Switching to branch {args.name}")
        checkout_branch(args)
    else:
        list_branches()

def diff(args):
    from vctrl.commands.diff import diff
    diff()
    print("Diff complete")

def merge(args):
    from vctrl.commands.merge import merge
    merge(args.base, args.other)
    print(f"Merged {args.other} into {args.base}")

def fetch(args):
    from vctrl.commands.fetch import fetch
    fetch(args.remote)
    print(f"Fetched from {args.remote}")

def init(args):
    from vctrl.repo import init
    path = init(args.path)

def build_parser():
    parser = argparse.ArgumentParser(prog='vctrl', description="Git-like version control tool")
    subparsers = parser.add_subparsers(title='subcommands', dest='command')

    subparsers.add_parser("login").add_argument("--server", required=True)
    login_parser = subparsers.choices["login"]
    login_parser.add_argument("--username", required=True)
    login_parser.add_argument("--password", required=True)
    login_parser.set_defaults(func=login)

    subparsers.add_parser("init", help="Initialize a repo").add_argument("path", nargs='?', default=os.getcwd())
    subparsers.choices["init"].set_defaults(func=init)

    add_parser = subparsers.add_parser("add", help="Add a file to index")
    add_parser.add_argument("path")
    add_parser.set_defaults(func=add)

    commit_parser = subparsers.add_parser("commit", help="Commit changes")
    commit_parser.add_argument("-m", "--message", required=True)
    commit_parser.set_defaults(func=commit)

    checkout_parser = subparsers.add_parser("checkout", help="Checkout branch or commit")
    checkout_parser.add_argument("name")
    checkout_parser.set_defaults(func=checkout_branch)

    branch_parser = subparsers.add_parser("branch", help="Create/list/switch branches")
    branch_parser.add_argument("name", nargs="?", help="Branch name")
    branch_parser.add_argument("-b", "--create", action="store_true", help="Create new branch")
    branch_parser.set_defaults(func=handle_branch)
    status_parser = subparsers.add_parser("status", help="Show current branch")
    status_parser.set_defaults(func=status)

    diff_parser = subparsers.add_parser("diff", help="Show diff")
    diff_parser.set_defaults(func=diff)

    merge_parser = subparsers.add_parser("merge", help="Merge branches")
    merge_parser.add_argument("base")
    merge_parser.add_argument("other")
    merge_parser.set_defaults(func=merge)

    fetch_parser = subparsers.add_parser("fetch", help="Fetch from remote")
    fetch_parser.add_argument("remote")
    fetch_parser.set_defaults(func=fetch)

    push_parser = subparsers.add_parser("push", help="Push to remote")
    push_parser.add_argument("remote")
    push_parser.set_defaults(func=push)

    pull_parser = subparsers.add_parser("pull", help="Pull from remote")
    pull_parser.add_argument("remote")
    pull_parser.set_defaults(func=pull)

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

