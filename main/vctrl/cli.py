#!/usr/bin/env python3

import argparse, os, json, sys
from vctrl.commands.branch import create_branch, list_branches

def status(args):
    from vctrl.refs import get_ref, get_branch_name
    branch = get_branch_name()
    if branch:
        print(f"📍 You are on branch: {branch}")
    else:
        commit_oid = get_ref("HEAD")
        print(f"📍 HEAD detached at {commit_oid[:7]}")

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
    from vctrl.refs import get_ref, update_ref
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
        update_ref(ref[5:], oid)
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
    from vctrl.commands.diff import diff_index_vs_workdir
    diff_index_vs_workdir()
    print("Diff complete")

def merge_command(args):
    from vctrl.refs import get_ref
    base_oid = get_ref(f"refs/heads/{args.base}")
    other_oid = get_ref(f"refs/heads/{args.other}")
    from vctrl.commands.merge import merge
    merge(base_oid, other_oid)

def init(args):
    from vctrl.repo import init
    path = init(args.path)

def build_parser():
    parser = argparse.ArgumentParser(prog='vctrl', description="Git-like version control tool")
    subparsers = parser.add_subparsers(title='subcommands', dest='command')

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
    merge_parser.set_defaults(func=merge_command)

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
