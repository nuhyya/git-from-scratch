# test_commands.py — FIXED
import os
import pytest
from unittest.mock import patch, mock_open, MagicMock, call

# ---------------------------
# TestBranch
# ---------------------------
class TestBranch:

    @patch('vctrl.commands.branch.update_ref')
    @patch('builtins.print')
    def test_create_branch_with_start_oid(self, mock_print, mock_update_ref):
        from vctrl.commands.branch import create_branch
        create_branch("feature", start_oid="abc123")
        mock_update_ref.assert_called_once_with("refs/heads/feature", "abc123")
        mock_print.assert_called_once_with("Branch 'feature' created at abc123")

    @patch('vctrl.commands.branch.get_ref')
    @patch('vctrl.commands.branch.update_ref')
    @patch('builtins.print')
    def test_create_branch_without_start_oid_with_symbolic_ref(self, mock_print, mock_update_ref, mock_get_ref):
        from vctrl.commands.branch import create_branch
        mock_get_ref.side_effect = ["ref: refs/heads/main", "abc456"]
        create_branch("feature")
        mock_update_ref.assert_called_once_with("refs/heads/feature", "abc456")
        assert mock_get_ref.call_count == 2

    @patch('vctrl.commands.branch.get_ref')
    @patch('vctrl.commands.branch.update_ref')
    @patch('builtins.print')
    def test_create_branch_without_start_oid_with_direct_oid(self, mock_print, mock_update_ref, mock_get_ref):
        from vctrl.commands.branch import create_branch
        mock_get_ref.return_value = "789def"
        create_branch("testbranch")
        mock_update_ref.assert_called_once_with("refs/heads/testbranch", "789def")

    @patch('vctrl.commands.branch.get_ref')
    @patch('vctrl.commands.branch.update_ref')
    def test_create_branch_empty_name(self, mock_update_ref, mock_get_ref):
        from vctrl.commands.branch import create_branch
        with pytest.raises(ValueError):
            create_branch("")
        mock_update_ref.assert_not_called()

    @patch('vctrl.commands.branch.update_ref')
    @patch('vctrl.commands.branch.get_ref', return_value="abc123")
    @patch('builtins.print')
    def test_create_branch_special_characters(self, mock_print, mock_get_ref, mock_update_ref):
        from vctrl.commands.branch import create_branch
        create_branch("feat/🔥-update")
        mock_update_ref.assert_called_once()

    @patch('os.listdir', return_value=["main", "dev"])
    @patch('builtins.print')
    @patch('vctrl.commands.branch.repo_path', return_value="/mock/.vctrl")
    def test_list_branches_success(self, mock_repo, mock_print, mock_listdir):
        from vctrl.commands.branch import list_branches
        list_branches()
        mock_print.assert_has_calls([call("main"), call("dev")])

# ---------------------------
# TestCheckout
# ---------------------------
class TestCheckout:

    @patch('builtins.open', new_callable=mock_open)
    @patch('vctrl.commands.checkout.clear_index')
    @patch('vctrl.commands.checkout.checkout_tree')
    @patch('vctrl.commands.checkout.GitObject.from_file')
    @patch('vctrl.commands.checkout.get_ref', return_value="commit123")
    @patch('vctrl.commands.checkout.repo_path', return_value="/mock/.vctrl")
    def test_checkout_branch_success(self, mock_repo, mock_get_ref, mock_from_file, mock_checkout_tree, mock_clear, mock_open_func):
        from vctrl.commands.checkout import checkout
        mock_from_file.return_value.data = b"tree123\nmessage"
        checkout("main")
        mock_checkout_tree.assert_called_once_with("tree123")
        mock_clear.assert_called_once()

    @patch('builtins.open', new_callable=mock_open)
    @patch('vctrl.commands.checkout.clear_index')
    @patch('vctrl.commands.checkout.checkout_tree')
    @patch('vctrl.commands.checkout.GitObject.from_file')
    @patch('vctrl.commands.checkout.repo_path', return_value="/mock/.vctrl")
    def test_checkout_direct_oid(self, mock_repo, mock_from_file, mock_checkout_tree, mock_clear, mock_open_func):
        from vctrl.commands.checkout import checkout
        mock_from_file.return_value.data = b"tree456\nmessage"
        checkout("commit456")
        mock_checkout_tree.assert_called_once_with("tree456")

    @patch('builtins.open', new_callable=mock_open)
    @patch('vctrl.commands.checkout.os.makedirs')
    @patch('vctrl.commands.checkout.GitObject.from_file')
    def test_checkout_tree_success(self, mock_from_file, mock_makedirs, mock_open_func):
        from vctrl.commands.checkout import checkout_tree
        mock_tree = MagicMock()
        mock_tree.data = b"100644 file.txt abc123"
        mock_from_file.return_value = mock_tree
        mock_blob = MagicMock()
        mock_blob.data = b"hello"
        mock_from_file.side_effect = [mock_tree, mock_blob]
        checkout_tree("tree123")
        assert mock_from_file.call_count == 2

    def test_checkout_tree_malformed_entry(self):
        from vctrl.commands.checkout import checkout_tree
        with patch('vctrl.commands.checkout.GitObject.from_file') as mock_from_file:
            # Provide only 1 part instead of 3 to trigger the ValueError
            mock_from_file.return_value.data = b"malformedentry"
            with pytest.raises(ValueError):
                checkout_tree("badtree")

# ---------------------------
# TestDiff
# ---------------------------
class TestDiff:

    @patch('vctrl.commands.diff.read_index', return_value={"file.txt": "abc123"})
    @patch('vctrl.commands.diff.GitObject.save', return_value="different")
    @patch('builtins.open', new_callable=mock_open, read_data=b"changed")
    @patch('builtins.print')
    def test_diff_modified_files(self, mock_print, mock_open_func, mock_save, mock_read):
        from vctrl.commands.diff import diff_index_vs_workdir
        diff_index_vs_workdir()
        mock_print.assert_called_once_with("Modified: file.txt")

    @patch('vctrl.commands.diff.read_index', return_value={"missing.txt": "abc123"})
    @patch('builtins.open', side_effect=FileNotFoundError)
    @patch('builtins.print')
    def test_diff_deleted_files(self, mock_print, mock_open_func, mock_read):
        from vctrl.commands.diff import diff_index_vs_workdir
        diff_index_vs_workdir()
        mock_print.assert_called_once_with("Deleted: missing.txt")

# ---------------------------
# TestFetch
# ---------------------------
class TestFetch:

    @patch('vctrl.commands.fetch.os.walk')
    @patch('vctrl.commands.fetch.shutil.copy2')
    @patch('vctrl.commands.fetch.os.makedirs')
    @patch('builtins.print')
    @patch('vctrl.commands.fetch.repo_path', return_value="/dest/repo/.vctrl")
    def test_fetch_success(self, mock_repo, mock_print, mock_makedirs, mock_copy2, mock_walk):
        from vctrl.commands.fetch import fetch
        mock_walk.return_value = [
            ("/source/repo/.vctrl/refs/heads", [], ["main", "feature"]),
            ("/source/repo/.vctrl/objects", [], ["obj1"]),
        ]
        fetch("/source/repo")
        assert mock_copy2.call_count >= 3
        mock_print.assert_called_once_with("Fetch complete.")

# ---------------------------
# TestMerge
# ---------------------------
class TestMerge:

    @patch('vctrl.commands.merge.checkout_tree')
    @patch('vctrl.commands.merge.write_index')
    @patch('vctrl.commands.merge.GitObject.from_file')
    @patch('builtins.print')
    def test_merge_success(self, mock_print, mock_from_file, mock_write, mock_checkout):
        from vctrl.commands.merge import merge
        base = MagicMock()
        base.data = b"treebase\nmessage"
        other = MagicMock()
        other.data = b"treeother\nmessage"
        mock_from_file.side_effect = [base, other]
        merge("base123", "other456")
        mock_checkout.assert_called_once_with("treeother")
        mock_write.assert_called_once_with({})
        mock_print.assert_called_once()

