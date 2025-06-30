# cli.py
from vctrl.commands.branch import create_branch, list_branches
import argparse, os, json
import requests

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
    print("Push complete")

def pull(args):
    from vctrl.remote import pull
    pull(args.remote, os.getcwd())
    print("Pull complete")

def clone(args):
    from vctrl.remote import clone
    clone(args.remote, args.dest)

def add(args):
    from vctrl.index import add
    add(args.file)

def commit(args):
    from vctrl.commit import commit
    commit(args.message)

def checkout(args):
    from vctrl.commands.checkout import checkout
    checkout(args.name)

def branch(args):
    from vctrl.commands.branch import create_branch, list_branches
    if args.name:
        create_branch(args.name)
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
    from vctrl.commands.init import init
    init()

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_login = subparsers.add_parser("login")
    parser_login.add_argument("--server")
    parser_login.add_argument("--username")
    parser_login.add_argument("--password")
    parser_login.set_defaults(func=login)

    parser_push = subparsers.add_parser("push")
    parser_push.add_argument("--remote")
    parser_push.set_defaults(func=push)

    parser_pull = subparsers.add_parser("pull")
    parser_pull.add_argument("--remote")
    parser_pull.set_defaults(func=pull)

    parser_clone = subparsers.add_parser("clone")
    parser_clone.add_argument("--remote")
    parser_clone.add_argument("--dest")
    parser_clone.set_defaults(func=clone)

    parser_add = subparsers.add_parser("add")
    parser_add.add_argument("file")
    parser_add.set_defaults(func=add)

    parser_commit = subparsers.add_parser("commit")
    parser_commit.add_argument("message")
    parser_commit.set_defaults(func=commit)

    parser_checkout = subparsers.add_parser("checkout")
    parser_checkout.add_argument("name")
    parser_checkout.set_defaults(func=checkout)

    parser_branch = subparsers.add_parser("branch")
    parser_branch.add_argument("--name", default=None)
    parser_branch.set_defaults(func=branch)

    parser_diff = subparsers.add_parser("diff")
    parser_diff.set_defaults(func=diff)

    parser_merge = subparsers.add_parser("merge")
    parser_merge.add_argument("base")
    parser_merge.add_argument("other")
    parser_merge.set_defaults(func=merge)

    parser_fetch = subparsers.add_parser("fetch")
    parser_fetch.add_argument("remote")
    parser_fetch.set_defaults(func=fetch)

    parser_init = subparsers.add_parser("init")
    parser_init.set_defaults(func=init)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

