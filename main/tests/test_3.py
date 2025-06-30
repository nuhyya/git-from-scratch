# test_remote_auth_cli.py
import os
import tempfile
import pytest
import json
from unittest import mock
from vctrl.remote import push, pull, clone
from vctrl.auth_server import app, init_db
import vctrl.cli
import builtins


@pytest.fixture(scope="session", autouse=True)
def clear_auth_db():
    try:
        os.remove("users.db")
    except FileNotFoundError:
        pass


# ---- Remote Tests ----
@mock.patch("vctrl.remote.requests.post")
@mock.patch("os.walk")
@mock.patch("builtins.open", new_callable=mock.mock_open, read_data="abc123")
def test_push(mock_open, mock_walk, mock_post):
    mock_walk.return_value = [
        ("/repo/.vctrl/refs/heads", [], ["main"]),
        ("/repo/.vctrl/objects", [], ["abc123"])
    ]
    push("http://example.com", "/repo")
    assert mock_post.call_count >= 2

@mock.patch("vctrl.remote.requests.get")
@mock.patch("builtins.open", new_callable=mock.mock_open)
@mock.patch("os.makedirs")
def test_pull(mock_makedirs, mock_open, mock_get):
    mock_get.side_effect = [
        mock.Mock(json=lambda: {"refs/heads/main": "abc123"}),
        mock.Mock(json=lambda: {"abc123": "626364"})
    ]
    pull("http://example.com", "/repo")
    assert mock_open.call_count >= 2

@mock.patch("vctrl.remote.pull")
@mock.patch("os.makedirs")
def test_clone(mock_makedirs, mock_pull):
    clone("http://example.com", "/new_repo")
    mock_pull.assert_called_once()


# ---- Auth Server Tests ----
@pytest.fixture
def client():
    app.config['TESTING'] = True
    init_db()
    with app.test_client() as client:
        yield client

def test_signup_new_user(client):
    res = client.post("/signup", json={"username": "bob11", "email": "bob11@example.com", "password": "bobpass"})
    assert res.status_code == 201

def test_login_after_signup(client):
    client.post("/signup", json={"username": "bob1", "email": "bob1@example.com", "password": "bobpass"})
    res = client.post("/login", json={"username": "bob1", "password": "bobpass"})
    assert res.status_code == 200
    assert "token" in res.json

def test_login_invalid(client):
    res = client.post("/login", json={"username": "ghost", "password": "wrong"})
    assert res.status_code == 401

def test_duplicate_signup(client):
    client.post("/signup", json={"username": "alice", "email": "a@example.com", "password": "pass"})
    res = client.post("/signup", json={"username": "alice", "email": "a@example.com", "password": "pass"})
    assert res.status_code == 409

def test_repo_access(client):
    client.post("/signup", json={"username": "tim", "email": "t@example.com", "password": "secret"})
    res = client.post("/login", json={"username": "tim", "password": "secret"})
    token = res.json['token']
    res = client.get("/repos/tim", headers={"Authorization": token})
    assert res.status_code == 200


def test_repo_access_denied(client):
    client.post("/signup", json={"username": "eve", "email": "e@example.com", "password": "pass"})
    res = client.post("/login", json={"username": "eve", "password": "pass"})
    token = res.json['token']
    res = client.get("/repos/not_eve", headers={"Authorization": token})
    assert res.status_code == 403


# ---- CLI Tests ----
@mock.patch("requests.post")
@mock.patch("builtins.open", new_callable=mock.mock_open)
def test_cli_login(mock_open, mock_post):
    mock_post.return_value = mock.Mock(status_code=200, json=lambda: {"token": "abc.def.ghi"})
    args = mock.Mock(server="http://localhost:5000", username="u", password="p")
    vctrl.cli.login(args)
    mock_open().write.assert_called()

@mock.patch("vctrl.remote.push")
def test_cli_push(mock_push):
    args = mock.Mock(remote="http://localhost:5000")
    vctrl.cli.push(args)
    mock_push.assert_called_once()

@mock.patch("vctrl.remote.pull")
def test_cli_pull(mock_pull):
    args = mock.Mock(remote="http://localhost:5000")
    vctrl.cli.pull(args)
    mock_pull.assert_called_once()

@mock.patch("vctrl.remote.clone")
def test_cli_clone(mock_clone):
    args = mock.Mock(remote="http://localhost:5000", dest="./repo")
    vctrl.cli.clone(args)
    mock_clone.assert_called_once()

@mock.patch("vctrl.cli.list_branches")
def test_cli_branch_list(mock_list):
    args = mock.Mock()
    args.name = None
    vctrl.cli.branch(args)
    mock_list.assert_called_once()

@mock.patch("vctrl.commands.branch.repo_path", return_value="/mock/repo")
@mock.patch("os.listdir", return_value=["main", "dev"])
@mock.patch("os.path.exists", return_value=True)
@mock.patch("builtins.open", new_callable=mock.mock_open, read_data="ref: refs/heads/main")
def test_cli_branch_list(mock_open, mock_exists, mock_listdir, mock_repo_path, capsys):
    args = mock.Mock()
    args.name = None
    vctrl.cli.branch(args)
    output = capsys.readouterr().out
    assert "main" in output
    assert "dev" in output
