import pytest
import os
import json
import tempfile
import shutil
from unittest.mock import patch

# Import your modules
from vctrl import repo, index, objects, refs


class TestRepo:
    
    def test_repo_path(self):
        """Test repo_path returns correct path"""
        expected = os.path.join(os.getcwd(), ".vctrl")
        assert repo.repo_path() == expected
    
    def test_init_creates_directories(self):
        """Test init creates required directory structure"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('os.getcwd', return_value=temp_dir):
                repo_dir = repo.init()
                
                assert os.path.exists(os.path.join(repo_dir, "refs"))
                assert os.path.exists(os.path.join(repo_dir, "objects"))
                assert os.path.exists(os.path.join(repo_dir, "HEAD"))
                
                with open(os.path.join(repo_dir, "HEAD")) as f:
                    assert f.read() == "ref: refs/heads/main"


class TestIndex:
    
    def setup_method(self):
        """Setup temporary directory for each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.vctrl_dir = os.path.join(self.temp_dir, ".vctrl")
        os.makedirs(self.vctrl_dir, exist_ok=True)
        
    def teardown_method(self):
        """Cleanup after each test"""
        shutil.rmtree(self.temp_dir)
    
    def test_read_index_empty(self):
        """Test reading index when file doesn't exist"""
        with patch('vctrl.repo.repo_path', return_value=self.vctrl_dir):
            result = index.read_index()
            assert result == {}
    
    def test_read_index_existing(self):
        """Test reading existing index file"""
        test_data = {"file1.txt": "abc123", "file2.txt": "def456"}
    
        with patch('vctrl.repo.repo_path', return_value=self.vctrl_dir):
            index_file = os.path.join(self.vctrl_dir, "index")
            os.makedirs(os.path.dirname(index_file), exist_ok=True)

            with open(index_file, 'w') as f:
                json.dump(test_data, f)

            result = index.read_index()
   
    @patch('vctrl.index.repo_path')  # ✅ Patch where it's actually used
    def test_write_index(self, mock_repo_path):
        """Test writing index to file"""
        test_data = {"file1.txt": "abc123"}

        mock_repo_path.return_value = self.vctrl_dir  # ✅ Ensure .vctrl path resolves correctly
        os.makedirs(self.vctrl_dir, exist_ok=True)

        # Act
        index.write_index(test_data)

        # Assert
        index_file = os.path.join(self.vctrl_dir, "index")
        assert os.path.exists(index_file)

        with open(index_file) as f:
            result = json.load(f)

        assert result == test_data
  
    def test_add_to_index_new_entry(self):
        """Test adding new entry to index"""
        with patch('vctrl.repo.repo_path', return_value=self.vctrl_dir):
            index.clear_index()
            index.add_to_index("test.txt", "abc123")
            
            result = index.read_index()
            assert result == {"test.txt": "abc123"}
    
    def test_add_to_index_update_existing(self):
        """Test updating existing entry in index"""
        # Setup existing index
        initial_data = {"test.txt": "old_hash"}
        with patch('vctrl.repo.repo_path', return_value=self.vctrl_dir):
            index.write_index(initial_data)
            
            # Update entry
            index.add_to_index("test.txt", "new_hash")
            
            result = index.read_index()
            assert result == {"test.txt": "new_hash"}
    
    def test_add_to_index_invalid_file_path(self):
        """Test add_to_index with invalid file path"""
        with pytest.raises(TypeError, match="Invalid file path"):
            index.add_to_index("", "abc123")
        
        with pytest.raises(TypeError, match="Invalid file path"):
            index.add_to_index("   ", "abc123")
        
        with pytest.raises(TypeError, match="Invalid file path"):
            index.add_to_index(None, "abc123")
    
    def test_add_to_index_invalid_oid(self):
        """Test add_to_index with invalid object ID"""
        with pytest.raises(TypeError, match="Invalid object ID"):
            index.add_to_index("test.txt", "")
        
        with pytest.raises(TypeError, match="Invalid object ID"):
            index.add_to_index("test.txt", "   ")
        
        with pytest.raises(TypeError, match="Invalid object ID"):
            index.add_to_index("test.txt", None)
    
    def test_clear_index(self):
        """Test clearing index"""
        # Setup index with data
        with patch('vctrl.repo.repo_path', return_value=self.vctrl_dir):
            index.add_to_index("test.txt", "abc123")
            assert index.read_index() == {"test.txt": "abc123"}
            
            # Clear index
            index.clear_index()
            assert index.read_index() == {}
class TestObjects:
    
    def setup_method(self):
        """Setup temporary directory for each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.vctrl_dir = os.path.join(self.temp_dir, ".vctrl")
        self.objects_dir = os.path.join(self.vctrl_dir, "objects")
        os.makedirs(self.objects_dir, exist_ok=True)
        
    def teardown_method(self):
        """Cleanup after each test"""
        shutil.rmtree(self.temp_dir)
    
    def test_hash_object(self):
        """Test hash_object creates correct hash and file"""
        test_data = b"hello world"
        
        with patch('vctrl.objects.repo_path', return_value=self.vctrl_dir):
            oid = objects.hash_object(test_data)
            
            # Verify hash format
            assert len(oid) == 40
            assert all(c in '0123456789abcdef' for c in oid)
            
            # Verify file was created
            object_path = os.path.join(self.objects_dir, oid)
            assert os.path.exists(object_path)
    
    def test_hash_object_no_objects_dir(self):
        """Test hash_object raises error when objects directory doesn't exist"""
        test_data = b"hello world"
        temp_dir_no_objects = tempfile.mkdtemp()
        vctrl_no_objects = os.path.join(temp_dir_no_objects, ".vctrl")
        os.makedirs(vctrl_no_objects)  # Create .vctrl but not objects
        
        try:
            with patch('vctrl.objects.repo_path', return_value=vctrl_no_objects):
                with pytest.raises(FileNotFoundError, match="Object directory not found"):
                    objects.hash_object(test_data)
        finally:
            shutil.rmtree(temp_dir_no_objects)
    
    def test_get_object(self):
        """Test get_object retrieves correct data"""
        test_data = b"hello world"
        
        with patch('vctrl.objects.repo_path', return_value=self.vctrl_dir):
            oid = objects.hash_object(test_data)
            retrieved_data = objects.get_object(oid)
            
            assert retrieved_data == test_data
    
    def test_get_object_with_type_check(self):
        """Test get_object with type verification"""
        test_data = b"hello world"
        
        with patch('vctrl.objects.repo_path', return_value=self.vctrl_dir):
            oid = objects.hash_object(test_data, "blob")
            retrieved_data = objects.get_object(oid, "blob")
            
            assert retrieved_data == test_data
    
    def test_get_object_wrong_type(self):
        """Test get_object fails with wrong expected type"""
        test_data = b"hello world"
        
        with patch('vctrl.objects.repo_path', return_value=self.vctrl_dir):
            oid = objects.hash_object(test_data, "blob")
            
            with pytest.raises(AssertionError):
                objects.get_object(oid, "tree")
    
    def test_blob_creation(self):
        """Test Blob object creation"""
        test_data = b"test content"
        blob = objects.Blob(data=test_data)
        
        assert blob.type == "blob"
        assert blob.data == test_data
        assert blob.oid is None
    
    def test_blob_from_file_path(self):
        """Test creating Blob from file path"""
        test_content = b"file content"
        test_file = os.path.join(self.temp_dir, "test.txt")
        
        with open(test_file, 'wb') as f:
            f.write(test_content)
        
        blob = objects.Blob.from_file_path(test_file)
        assert blob.data == test_content
        assert blob.type == "blob"
    
    def test_blob_save(self):
        """Test saving blob object"""
        test_data = b"test content"
        blob = objects.Blob(data=test_data)
        
        with patch('vctrl.objects.repo_path', return_value=self.vctrl_dir):
            oid = blob.save()
            
            assert blob.oid == oid
            assert len(oid) == 40
    
    def test_blob_save_no_data(self):
        """Test saving blob with no data raises error"""
        blob = objects.Blob()
        
        with pytest.raises(ValueError, match="Cannot save object with no data"):
            blob.save()
    
    def test_tree_creation_empty(self):
        """Test creating empty Tree object"""
        tree = objects.Tree()
        
        assert tree.type == "tree"
        assert tree.entries == []
        # Empty tree should have empty data
        assert tree.data == b"" or tree.data is None
    
    def test_tree_with_entries(self):
        """Test creating Tree with entries"""
        entries = [("blob", "abc123", "file1.txt"), ("tree", "def456", "subdir")]
        tree = objects.Tree(entries=entries)
        
        assert tree.entries == entries
        assert tree.type == "tree"
        assert b"blob abc123 file1.txt" in tree.data
        assert b"tree def456 subdir" in tree.data
    
    def test_tree_add_entry(self):
        """Test adding entry to tree"""
        tree = objects.Tree()
        tree.add_entry("blob", "abc123", "test.txt")
        
        assert len(tree.entries) == 1
        assert tree.entries[0] == ("blob", "abc123", "test.txt")
        assert b"blob abc123 test.txt" in tree.data
    
    def test_tree_from_directory(self):
        """Test creating tree from directory structure"""
        # Create test files
        test_work_dir = os.path.join(self.temp_dir, "work")
        os.makedirs(test_work_dir)
        os.makedirs(os.path.join(test_work_dir, "subdir"))
        
        with open(os.path.join(test_work_dir, "file1.txt"), 'w') as f:
            f.write("content1")
        
        with open(os.path.join(test_work_dir, "subdir", "file2.txt"), 'w') as f:
            f.write("content2")
        
        with patch('vctrl.objects.repo_path', return_value=self.vctrl_dir):
            tree = objects.Tree.from_directory(test_work_dir)
            
            # Should have entries for file1.txt and subdir
            assert len(tree.entries) == 2
            
            # Check entries exist (order may vary)
            entry_names = [entry[2] for entry in tree.entries]
            assert "file1.txt" in entry_names
            assert "subdir" in entry_names
    
    def test_tree_from_directory_skips_vctrl(self):
        """Test tree creation skips .vctrl directory"""
        # Create .vctrl directory and regular file in work directory
        test_work_dir = os.path.join(self.temp_dir, "work")
        os.makedirs(test_work_dir)
        os.makedirs(os.path.join(test_work_dir, ".vctrl"))
        
        with open(os.path.join(test_work_dir, "file1.txt"), 'w') as f:
            f.write("content1")
        
        with patch('vctrl.objects.repo_path', return_value=self.vctrl_dir):
            tree = objects.Tree.from_directory(test_work_dir)
            
            # Should only have file1.txt, not .vctrl
            assert len(tree.entries) == 1
            assert tree.entries[0][2] == "file1.txt"
    
    def test_commit_creation(self):
        """Test Commit object creation"""
        tree_oid = "abc123"
        message = "Initial commit"
        
        commit = objects.Commit(tree_oid=tree_oid, message=message)
        
        assert commit.type == "commit"
        assert commit.tree_oid == tree_oid
        assert commit.message == message
        assert commit.author_name == "you"
        assert commit.author_email == "notknown"
        assert b"tree abc123" in commit.data
        assert b"Initial commit" in commit.data
    
    def test_commit_with_parent(self):
        """Test Commit creation with parent"""
        tree_oid = "abc123"
        parent_oid = "def456"
        
        commit = objects.Commit(tree_oid=tree_oid, parent=parent_oid)
        
        assert commit.parent == parent_oid
        assert b"parent def456" in commit.data
    
    def test_commit_no_tree_oid(self):
        """Test Commit creation fails without tree_oid"""
        with pytest.raises(ValueError, match="Cannot create a commit with no tree"):
            objects.Commit(tree_oid=None)
    
    def test_write_tree_function(self):
        """Test write_tree convenience function"""
        # Create test file in work directory
        test_work_dir = os.path.join(self.temp_dir, "work")
        os.makedirs(test_work_dir)
        
        with open(os.path.join(test_work_dir, "test.txt"), 'w') as f:
            f.write("content")
        
        with patch('vctrl.objects.repo_path', return_value=self.vctrl_dir):
            oid = objects.write_tree(test_work_dir)
            
            assert oid is not None
            assert len(oid) == 40
    
    def test_write_tree_empty_directory(self):
        """Test write_tree with empty directory"""
        empty_dir = os.path.join(self.temp_dir, "empty")
        os.makedirs(empty_dir)
        
        with patch('vctrl.objects.repo_path', return_value=self.vctrl_dir):
            oid = objects.write_tree(empty_dir)
            
            assert oid is None


class TestRefs:
    
    def setup_method(self):
        """Setup temporary directory for each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.vctrl_dir = os.path.join(self.temp_dir, ".vctrl")
        self.refs_dir = os.path.join(self.vctrl_dir, "refs", "heads")
        os.makedirs(self.refs_dir, exist_ok=True)
        
    def teardown_method(self):
        """Cleanup after each test"""
        shutil.rmtree(self.temp_dir)
    
    def test_update_ref(self):
        """Test updating reference"""
        test_oid = "abc123def456"
        ref_name = "refs/heads/main"
        
        with patch('vctrl.refs.repo_path', return_value=self.vctrl_dir):
            refs.update_ref(ref_name, test_oid)
            
            # Verify file was created with correct content
            ref_path = os.path.join(self.vctrl_dir, ref_name)
            with open(ref_path) as f:
                assert f.read() == test_oid
    
    def test_get_ref(self):
        """Test getting reference"""
        test_oid = "abc123def456"
        ref_name = "refs/heads/main"
        
        # Create ref file
        ref_path = os.path.join(self.vctrl_dir, ref_name)
        
        with open(ref_path, 'w') as f:
            f.write(test_oid)
        
        # Test getting ref
        with patch('vctrl.refs.repo_path', return_value=self.vctrl_dir):
            result = refs.get_ref(ref_name)
            assert result == test_oid
    
    def test_get_ref_with_whitespace(self):
        """Test getting reference strips whitespace"""
        test_oid = "abc123def456"
        ref_name = "refs/heads/main"
        
        # Create ref file with whitespace
        ref_path = os.path.join(self.vctrl_dir, ref_name)
        
        with open(ref_path, 'w') as f:
            f.write(f"  {test_oid}  \n")
        
        # Test getting ref
        with patch('vctrl.refs.repo_path', return_value=self.vctrl_dir):
            result = refs.get_ref(ref_name)
            assert result == test_oid
